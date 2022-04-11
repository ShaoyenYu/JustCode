import io
import re
from multiprocessing.dummy import Pool as ThreadPool
from queue import PriorityQueue, Queue, Empty
from threading import Thread, Event

from telegram import (
    Update, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, )
from telegram.ext import (
    CallbackContext, Updater, MessageHandler, CallbackQueryHandler,
    Filters
)

from lib import libgen
from lib.tgbot.bots.ebook_downloader import Command, Task, CallbackUpdate, CONFIG
from lib.tgbot.ext import TextBuilder, ValidUserFilter
from util.concurrent import KillableThread

valid_user_filter = ValidUserFilter(valid_users=CONFIG["Users"]["ValidUsers"])

SYS_REBOOT = Command(0, "SYS_REBOOT")
SYS_STOP_ALL = Command(1, "SYS_STOP_ALL")
CMD_QUESTION_MARK = Command(10, "CMD_QUESTION_MARK")


def image_to_byte_array(image):
    image_byte_array = io.BytesIO()
    image.save(image_byte_array, format=image.format)
    image_byte_array = image_byte_array.getvalue()
    return image_byte_array


class UserCallback:
    class Session:
        _name = "Session"

        dialog = "cb.session.dialog."

    class Ebook:
        _name = "Ebook"

        class Inputting:
            listening = "cb.ebook.inputting.listening"
            cancel = "cb.ebook.inputting.cancel"

        class Result:
            cache = "cb.ebook.result.cache"


class ReplyKeyboardButtons:
    btn_search_by_isbn = KeyboardButton(
        "🌟 Search by ISBN/Title", callback_data="Btn.SearchBook",
    )
    btn_cancel_search = KeyboardButton("        👋 Quit        ", callback_data="Btn.SearchCancel")


VALID_TEXT = {ReplyKeyboardButtons.btn_search_by_isbn.text, ReplyKeyboardButtons.btn_cancel_search.text}


class InlineKeyboardButtons:
    btn_search_by_isbn = InlineKeyboardButton("Search by ISBN/Title", callback_data="Btn.SearchBook")
    btn_cancel_search = InlineKeyboardButton("Cancel", callback_data="Btn.SearchCancel")


class Job:
    def __init__(self, updater: Updater, pool_num):
        self.pool_num = pool_num
        self.updater = updater

        self.task_queue = Queue()
        self._task_manager = Thread(target=self.loop_manage_tasks, name="T-task_killer")

        self.message_queue = Queue()
        self._message_parser = Thread(target=self.loop_parse_message, name="T-message_parser")

        self.manage_queue = PriorityQueue()
        self._worker_manager = Thread(target=self.loop_manage_workers, name="T-worker_manager")
        self._worker_manager.can_receive_new = Event()

        self.download_queue = Queue()
        self.download_pool = ThreadPool(self.pool_num)

        self.result_handler = Thread(target=self.loop_handle_result, name="T-result_handler")

        self.pool_num = pool_num
        self._task_workers = []

        self.session = dict()

    def start(self):
        self.result_handler.start()
        self._task_manager.start()
        self._worker_manager.can_receive_new.set()
        self._worker_manager.start()
        self._message_parser.start()

    def inqueue_downloader(self, func, queue=None):
        if queue is None:
            queue = self.download_queue

        def wrapper(*args, **kwargs):
            res = func(*args, **kwargs)
            queue.put(res)
            return res

        return wrapper

    # specific job
    def _callback_request_search(self, msg):
        # msg.context.bot.delete_message(
        #     chat_id=msg.update.message.chat_id,
        #     message_id=msg.update.message.message_id,
        #     # text="❤ OK, Just enter book name/ISBN: ❤"
        # )
        1 == 1
        msg.context.bot.send_message(
            chat_id=msg.update.message.chat_id,
            text="OK, please input a book name/ISBN:"
        )
        self.session \
            .setdefault(msg.update.message.from_user.id, dict()) \
            .setdefault(UserCallback.Ebook.__name__, dict()) \
            .update(**{UserCallback.Ebook.Inputting.listening: True})

        # msg.context.bot.answer_callback_query(msg.update.callback_query.id)

    def _callback_cancel_request_search(self, msg: CallbackUpdate):
        try:
            uid = msg.data["user_id"]
            del self.session[uid][f"{UserCallback.Ebook.__name__}"]
        except KeyError:
            pass
        msg.context.bot.edit_message_text(
            chat_id=msg.update.callback_query.message.chat_id,
            message_id=msg.update.callback_query.message.message_id,
            text="👋 Ok, Bye! 👋"
        )

    def _search_ebook_index(self, msg: CallbackUpdate):
        book = msg.update.message.text
        ucb = self.session[msg.data["user_id"]][UserCallback.Ebook.__name__]
        task = Task(
            libgen.LibgenDownloader.search_book, msg,
            book, ucb.setdefault("extension", None), ucb.setdefault("page", 1), ucb.setdefault("offset", 25),
            callback=self._organize_ebook_index, cb_args=(msg,)
        )

        self.download_pool.apply_async(self.inqueue_downloader(task), error_callback=print)

    def _organize_ebook_index(self, msg: CallbackUpdate):
        book_num, books = msg.data["result"]

        print(book_num, books)

        if book_num == 0:
            tb = TextBuilder()
            tb.add("不好意思，没有找到这本书.", type_="bold", newline=True)
            tb.add("Sorry, we didn't find this book.", type_="bold", newline=True)
            tb.add("Désolé, nous n'avons pas ce livre.", type_="bold", newline=True)
            tb.add("Tut mir leid, ich habe dieses Buch nicht gefunden.", type_="bold", newline=True)
            tb.add("申し訳ありませんが、この本はありません.", type_="bold", newline=True)
            tb.add("请重新输入书名/ISBN:", type_="bold", newline=True)
            msg.context.bot.send_message(
                chat_id=msg.update.effective_chat.id,
                text=tb.text,
                entities=tb.entities
            )

        else:
            self.session[msg.data["user_id"]][UserCallback.Ebook.__name__]["Cache"] = {}
            msg.context.bot.send_message(
                chat_id=msg.update.effective_chat.id,
                text=f"⭐ {book_num} books found in total:",
            )

            books_ = list(books.items())
            for i in range(0, len(books), 5):
                tb = TextBuilder()
                for j in range(i, min(i + 5, len(books))):
                    md5, book = books_[j]
                    print(j)
                    spaces = "    "
                    # tb.add(book["title"], type_="text_link", newline=True, url=f"https://api.telegram.org/bot{CONFIG['BotsToken']['S000']}/{sendMessage}")
                    # tb.add(book["title"], type_="text_link", newline=True, url=f"https://api.telegram.org/bot{CONFIG['BotsToken']['S000']}/{method}")
                    tb.add(book["title"], type_="bold", newline=True)
                    for k in ("author(s)", "year", "pages", "language", "size", "format"):
                        tb.add(f"{spaces}· {k[0].upper()}{k[1:]}: ", type_="bold", newline=False)
                        if isinstance(book[k], list):
                            tb.add(', '.join(book.get(k) or ""), type_="italic", newline=True)
                        else:
                            tb.add(book.get(k) or "", type_="italic", newline=True)

                    tb.add("", type_="bold", newline=True)

                msg.context.bot.send_message(
                    chat_id=msg.update.effective_chat.id,
                    # photo=image_to_byte_array(book_detail["thumbnail"]),
                    text=tb.text,
                    entities=tb.entities
                )
                1 == 1
            # msg.context.bot.send_photo(
            #     chat_id=msg.update.effective_chat.id,
            #     # photo=image_to_byte_array(book_detail["thumbnail"]),
            #     caption=tb.text,
            #     caption_entities=tb.entities
            # )

    # CMD commands
    def _handle_cmd_reboot(self, msg: CallbackUpdate):
        msg.context.bot.send_message(chat_id=msg.update.effective_chat.id, text="Rebooting...")
        msg.context.bot.send_message(chat_id=msg.update.effective_chat.id, text="😂")
        self.updater.stop()
        self.updater.start_polling()
        msg.context.bot.send_message(chat_id=msg.update.effective_chat.id, text="Completed...")
        msg.context.bot.send_message(chat_id=msg.update.effective_chat.id, text="😊")

    def _handle_cmd_stop(self):
        self._worker_manager.can_receive_new.clear()
        for worker in self._task_workers:
            worker.terminate()
            worker.join()

        while True:
            try:
                print("clearing cmd queue...")
                self.task_queue.get(timeout=5)

            except Empty:
                print("done!")
                break
        self._worker_manager.can_receive_new.set()

    def _handle_cmd_question_mark(self, msg):
        tb = TextBuilder()
        tb.add("❤ Looking for a book? ❤", type_="bold", newline=True)

        msg.context.bot.send_message(
            chat_id=msg.update.effective_chat.id,
            text=tb.text,
            reply_markup=ReplyKeyboardMarkup(
                resize_keyboard=True, one_time_keyboard=True, input_field_placeholder="我宝宝是猪",
                keyboard=[
                    [ReplyKeyboardButtons.btn_search_by_isbn, ReplyKeyboardButtons.btn_cancel_search],
                ]),
        )

    # handler thread functions
    def _parse_message(self, msg: CallbackUpdate):
        phrases = re.split(" |\.", msg.update.message.text if not msg.inline else msg.update.callback_query.data)
        try:
            print(f"{msg.update.message.text}")
            print(f"{msg.update.message.chat_id}, {msg.update.message.message_id}")
        except Exception as e:
            print(e)

        # handle normal message
        if phrases[0] == "SYS":
            if phrases[1] == "reboot":
                msg.data["cmd"] = SYS_REBOOT
                self.manage_queue.put(Task(self._handle_cmd_reboot, msg, msg=msg))

            elif phrases[1] == "stop":
                msg.data["cmd"] = SYS_STOP_ALL
                self.manage_queue.put(Task(self._handle_cmd_stop, msg))

        elif phrases[0] == "CMD":
            if phrases[1] == "?":
                msg.data["cmd"] = CMD_QUESTION_MARK
                self.task_queue.put(Task(self._handle_cmd_question_mark, msg, msg=msg))

        # This part handles Inline Button
        # elif phrases[0] == "Btn":
        #     if phrases[1] == "SearchBook":
        #         self.task_queue.put(Task(self._callback_request_search, msg, msg=msg))
        #     elif phrases[1] == "SearchCancel":
        #         self.task_queue.put(Task(self._callback_cancel_request_search, msg, msg=msg))
        else:
            # This part handles Common Button
            if msg.update.message.text in VALID_TEXT:
                if msg.update.message.text == ReplyKeyboardButtons.btn_search_by_isbn.text:
                    self.task_queue.put(Task(self._callback_request_search, msg, msg=msg))
                elif msg.update.message.text == ReplyKeyboardButtons.btn_cancel_search.text:
                    self.task_queue.put(Task(self._callback_cancel_request_search, msg, msg=msg))

            else:
                # This part handles Arbitrate Input
                user_id = msg.update.message.from_user.id
                user_session = self.session.get(user_id)
                if user_session is None or len(user_session) == 0:
                    return

                if (sess_ebook := user_session.get(f"{UserCallback.Ebook.__name__}")) is not None:
                    msg.data["user_id"] = user_id
                    for cb_type, cb_value in sess_ebook.items():
                        if cb_type == UserCallback.Ebook.Inputting.listening:
                            self.task_queue.put(Task(self._search_ebook_index, msg, msg=msg))

    def _repopulate_workers(self):
        print(len(self._task_workers), self._task_workers)
        if len(self._task_workers) < self.pool_num:
            try:
                task = self.task_queue.get(timeout=1)

            except Empty:
                pass
            else:
                if self._worker_manager.can_receive_new.is_set():
                    self._task_workers.append((worker := KillableThread(target=task)))
                    print(f"reach here1 {Task.f}")
                    worker.start()
                else:
                    print("dropping tasks...")
                    pass  # simply drop task

    def loop_handle_result(self):
        while True:
            result = self.download_queue.get()
            if isinstance(result, Task):
                self.task_queue.put(result)

    def loop_manage_tasks(self):
        while True:
            task = self.manage_queue.get()
            try:
                task()
            except Exception as e:
                print(e)

    def loop_manage_workers(self):
        while True:
            for i in reversed(range(len(self._task_workers))):
                if (worker := self._task_workers[i])._is_stopped:
                    worker.join()
                    del self._task_workers[i]
            self._repopulate_workers()

    def loop_parse_message(self):
        while True:
            if not self._worker_manager.can_receive_new.is_set():
                self.message_queue.get()
                print("dropping message...")
                continue

            msg = self.message_queue.get()
            try:
                self._parse_message(msg)
            except Exception as e:
                print(e)

    # lazy process: put message to queue
    def handle_msg_text(self, update: Update, context: CallbackContext):
        self.message_queue.put(CallbackUpdate(update, context))

    def handle_callback_query(self, update: Update, context: CallbackContext):
        self.message_queue.put(CallbackUpdate(update, context, inline=True))


if __name__ == '__main__':
    updater = Updater(token=CONFIG["BotsToken"]["S000"], use_context=True)

    job = Job(updater, 4)

    # handler_cmd_start = CommandHandler('hi', job.cmd_start)
    handler_msg_cmd_text = MessageHandler(valid_user_filter & Filters.text & (~Filters.command), job.handle_msg_text)
    handler_call_back_query = CallbackQueryHandler(job.handle_callback_query)

    # updater.dispatcher.add_handler(handler_cmd_start)
    updater.dispatcher.add_handler(handler_msg_cmd_text)
    updater.dispatcher.add_handler(handler_call_back_query)

    job.start()
    updater.start_polling()
