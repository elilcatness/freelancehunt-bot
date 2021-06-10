import os
from datetime import timedelta

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram.parsemode import ParseMode

from data import db_session
from data.mailing import Mail
from data.project import Project
from parse import FreelanceHunt


def job(context):
    bot = context.job.context.bot
    session = db_session.create_session()
    mail = session.query(Mail).get(context.job.context.user_data['chat_id'])
    parser = context.job.context.user_data['parser']
    updates = parser.get_updates(mail.projects[-1].id if mail.projects else None)
    if updates:
        new_projects = [Project(id=upd['id']) for upd in updates if upd['id']
                        not in [p.id for p in mail.projects]]
        mail.projects.extend(new_projects)
        if len(mail.projects) - 10 > 0:
            for _ in range(len(mail.projects) - 10):
                mail.projects.pop(0)
        session.merge(mail)
        session.commit()
    for update in filter(lambda x: x['id'] in [p.id for p in new_projects], updates[::-1]):
        message = '\n'.join([f'<b>{key}</b>: {val}' for key, val in list(update.items())[2:]])
        markup = InlineKeyboardMarkup([[InlineKeyboardButton('Открыть', url=update['url'])]])
        bot.send_message(mail.id, message, parse_mode=ParseMode.HTML,
                         disable_web_page_preview=True,
                         reply_markup=markup)
    session.close()


def start(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if context.job_queue.get_jobs_by_name(str(chat_id)):
        return update.message.reply_text('Рассылка уже включена')
    session = db_session.create_session()
    session.add(Mail(id=chat_id))
    session.commit()
    session.close()
    context.user_data['parser'] = FreelanceHunt(os.getenv('fh_token'))
    context.user_data['chat_id'] = chat_id
    update.message.reply_text('Рассылка успешно включена')
    context.job_queue.run_repeating(job, timedelta(seconds=120), timedelta(seconds=1),
                                    context=context, name=str(chat_id))


def stop(update, context):
    chat_id = update.message.chat_id
    session = db_session.create_session()
    mail = session.query(Mail).get(chat_id)
    if not mail:
        return update.message.reply_text('Рассылка не была включена')
    for job in context.job_queue.get_jobs_by_name(str(chat_id)):
        job.schedule_removal()
    for project in mail.projects:
        session.delete(project)
    session.delete(mail)
    session.commit()
    update.message.reply_text('Рассылка была успешно выключена')


def start_last_mails(dispatcher, bot):
    session = db_session.create_session()
    parser = FreelanceHunt(os.getenv('fh_token'))
    for mail in session.query(Mail).all():
        context = CallbackContext(dispatcher)
        context._bot = bot
        context._user_data = {'parser': parser, 'chat_id': mail.id}
        context.job_queue.run_repeating(job, timedelta(seconds=10), timedelta(seconds=1),
                                        context=context, name=str(mail.id))


def main():
    updater = Updater(os.getenv('tg_token'))
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('stop', stop))
    start_last_mails(updater.dispatcher, updater.bot)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    db_session.global_init(os.getenv('DATABASE_URL'))
    main()
