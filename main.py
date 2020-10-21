#!/usr/bin/env python3

import argparse
import os
from datetime import datetime
from time import sleep
from aion.kanban import KanbanConnection
from aion.logger import lprint
from aion.microservice import main_decorator, Options
import gi
from multiprocessing import Queue
from threading import Thread

gi.require_version('Gst', '1.0')  # noqa
from gi.repository import Gst, GLib  # isort:skip
# from gst_buffer_info_meta import write_meta, remove_meta, get_meta

SERVICE_NAME = "capture-movie-from-rtsp-daemon"
DEFAULT_SOURCE_URL = "rtsp://stream-usb-video-by-rtsp-001-srv:8555/usb"
DEFAULT_FPS = 10
LIMIT_MOVIE_LENGTH = 900

def get_pipe(source_url, output_path):
    gst_query = f"""
        rtspsrc location={source_url} name=rtsp !
        application/x-rtp, encoding-name=JPEG,payload=96 !
        rtpjpegdepay ! nvjpegdec ! video/x-raw ! nvvideoconvert !
        video/x-raw(memory:NVMM) ! nvv4l2h264enc !
        video/x-h264, stream-format=byte-stream !
        h264parse disable-passthrough=true ! mp4mux !
        filesink location={output_path}
        """
    pipe = Gst.parse_launch(gst_query)
    return pipe

class ConvertToMovieProcesss:
    def __init__(self, conn: KanbanConnection, data_path: str, source_url=DEFAULT_SOURCE_URL, num=1):
        self.state = False
        self.start_time = None
        self.end_time = None
        self.input_q = Queue()
        self.conn = conn
        self.data_path = data_path
        self.source_url = source_url
        self.num = num
        self.next_device = os.environ.get("NEXT_DEVICE")
        self.cm = None
        self.t = Thread(
            target=self.get_request_loop,
            args=(conn, self.input_q),
        )
        self.t.start()

    def __check_movie_length(self, current_time):
        length = current_time - datetime.strptime(self.start_time, "%Y%m%d%H%M%S%f")
        if length.total_seconds() > LIMIT_MOVIE_LENGTH:
            return True
        else:
            return False

    def get_request_loop(self, conn: KanbanConnection, queue: Queue):
        while True:
            try:
                data = queue.get()
                if self.state:
                    res = self.__check_movie_length(datetime.now())
                    if res:
                        self.cm.stop()
                        self.state = False
                if data.get("type") == "pre-start":
                    if self.state:
                        self.cm.stop()
                    self.output_path = self.__get_output_path()
                    self.cm = ConvertToMovie(self.source_url, self.output_path)
                    self.cm.start()
                    self.state = True
                    self.start_time = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
                    lprint("pre-start capture movie")
                elif data.get("type") == "start":
                    lprint("start capture movie")
                elif data.get("type") == "end":
                    self.cm.stop()
                    self.state = False
                    self.end_time = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
                    lprint(
                        "success capture movie {}".format(str(self.output_path))
                    )
                    self.__output_data()

                elif data.get("type") == "ready":
                    lprint("ready to capture-movie")
                else:
                    lprint(
                        "invalid type: {}".format(str(data.get("type")))
                    )
            except Exception as e:
                lprint(str(e))
            finally:
                pass

    def __get_output_path(self):
        if os.path.exists(self.data_path) == False:
            os.makedirs(self.data_path)
        date_str = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
        return os.path.join(self.data_path, date_str + ".mp4")

    def __output_data(self):
        output_data = {}
        output_data["start_time"] = self.start_time
        output_data["end_time"] = self.end_time
        output_data["file_name"] = os.path.basename(self.output_path)
        self.conn.output_kanban(
            file_list = [self.output_path],
            process_number=self.num,
            device_name = self.next_device,
            metadata=output_data,
        )
    
    def add_request(self, metadata: dict):
        self.input_q.put(metadata)

class ConvertToMovie:
    def __init__(self, source_url, output_path):
        self.success = False
        self.output_path = output_path
        self.loop = GLib.MainLoop()
        self.timeout_id = None
        self.length = None
        self.pipe = get_pipe(source_url, output_path)
        self.rtsp = self.pipe.get_by_name('rtsp')

        # set message trigger
        bus = self.pipe.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)

    def start(self):
        lprint("start capture and convert from rtsp...")
        self.pipe.set_state(Gst.State.PLAYING)
        # self.set_timeout()
        # print(f"start capture and convert from rtsp... (length:{self.length})")
        # self.loop.run()
        # return self.success

    def stop(self):
        self.rtsp.send_event(Gst.Event.new_eos())
        self.loop.quit()

    def unset_timeout(self):
        if self.timeout_id:
            GLib.source_remove(self.timeout_id)

    def set_timeout(self):
        self.timeout_id = GLib.timeout_add(self.length * 1000, self.timeout)

    def timeout(self):
        self.success = True
        self.stop()
        lprint(
            "[success] finish capture video (path: {}"
            .format(str(self.output_path))
        )

    def on_message(self, bus, message):
        if message.type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print(("Error received from element %s: %s" % (
                message.src.get_name(), err)))
            print(("Debugging information: %s" % debug))
            self.stop()
        elif message.type == Gst.MessageType.EOS:
            print("End-Of-Stream reached.")
            self.stop()
        elif message.type == Gst.MessageType.STATE_CHANGED:
            if isinstance(message.src, Gst.Pipeline):
                old_state, new_state, pending_state = message.parse_state_changed()
                print(("Pipeline state changed from %s to %s." %
                           (old_state.value_nick, new_state.value_nick)))

def argument_parser():
    parser = argparse.ArgumentParser(description='convert to movie from rtsp')

    parser.add_argument('-u', '--source-url', type=str,
                        default=DEFAULT_SOURCE_URL)

    return parser.parse_args()

@main_decorator(SERVICE_NAME)
def main(opt: Options):
    Gst.init(None)
    # for debug
    # Gst.debug_set_active(True)
    # Gst.debug_set_default_threshold(3)
    conn = opt.get_conn()
    num = opt.get_number()
    data_path = "/var/lib/aion/Data/capture-movie-from-rtsp-daemon_" + str(num)
    p = ConvertToMovieProcesss(conn, data_path=data_path, num=num)
    for kanban in conn.get_kanban_itr(SERVICE_NAME, num):
        metadata = kanban.get_metadata()
        p.add_request(metadata)
    
if __name__ == "__main__":
    main()
