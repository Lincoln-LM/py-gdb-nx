"""Wrapper around pygdbmi.GdbController for easier switch connection"""

from typing import Optional,List
import pygdbmi.gdbcontroller
import pygdbmi.constants

from .breakpoint import Breakpoint, WatchPoint


class GdbProcess(pygdbmi.gdbcontroller.GdbController):
    """Wrapper around pygdbmi.GdbController for easier switch connection"""
    def __init__(
        self,
        ip_address: str,
        breakpoints: Optional[List[Breakpoint]] = None,
        path_to_gdb: Optional[str] = "aarch64-none-elf-gdb.exe",
        time_to_check_for_additional_output_sec: float =
            pygdbmi.constants.DEFAULT_TIME_TO_CHECK_FOR_ADDITIONAL_OUTPUT_SEC,
    ):
        """
        Create new gdb process and connect to the switch

        Args:
            ip_address (str): Local IP address of the Nintendo Switch console

            breakpoints (Optional[List[Breakpoint]], optional): List of breakpoints
            to apply on start of process.

            path_to_gdb (Optional[str], optional): Path to gdb executable to run.
            Defaults to "aarch64-none-elf-gdb.exe"

            time_to_check_for_additional_output_sec (float, optional): When parsing responses,
            wait this amout of time before exiting (exits before timeout is reached to save time).
            If <= 0, full timeout time is used.
            Defaults to pygdbmi.constants.DEFAULT_TIME_TO_CHECK_FOR_ADDITIONAL_OUTPUT_SEC
        """
        super().__init__([path_to_gdb,"--interpreter=mi3"], time_to_check_for_additional_output_sec)
        self.ip_address = ip_address
        self.active_breakpoints = []
        self.main_base: int = None
        self.main_max: int = None
        self.heap_base: int = None
        self.heap_max: int = None
        self.stack_base: int = None
        self.stack_max: int = None
        self.bkpt_no = 1
        self.clear_responses()
        self.connect()
        self.attach()
        self.get_bases()
        self.write("set step-mode on")
        if breakpoints is not None:
            for item in breakpoints:
                self.add_breakpoint(item)

    def clear_responses(
        self,
    ):
        """
        Clear all cached gdb responses by sending an empty string
        """
        self.write("")

    def resume_execution(
        self,
    ):
        """
        Resume program execution by sending the continue command
        """
        self.write("continue")

    def connect(
        self,
    ):
        """
        Connect to the switch with the ip address stored in self.ip_address
        """
        self.write(f"target extended-remote {self.ip_address}:22225", read_response=False)
        self.log_response(self.wait_for_response())

    def attach(
        self,
        process_name: str = "Application",
    ):
        """Attach to process of name process_name

        Args:
            process_name (str, optional): Name of switch process to attach to.
            Defaults to "Application"
        """
        self.write("info os processes", read_response = False)
        processes = self.wait_for_response()
        for line in reversed(processes): # sort by latest process started
            if line['type'] == "console" and process_name in line["payload"]:
                process_id = int(line["payload"].split(" ",1)[0])
                self.log_response(self.write(f"attach {process_id}"))
                break

    def get_bases(
        self,
    ):
        """
        Read the base addresses of sections of the switch's memory
        """
        self.write("monitor get base", read_response = False)
        for line in self.filter_response(self.wait_for_response("target"), "target"):
            if "Heap" in line['payload']:
                self.heap_base, self.heap_max = \
                    (int(num, 16) for num in line['payload'].replace(" -","")[:-2].split(" ")[4:6])
            elif "Stack" in line['payload']:
                self.stack_base, self.stack_max = \
                    (int(num, 16) for num in line['payload'].replace(" -","")[:-2].split(" ")[3:5])
            elif ".nss" in line['payload']:
                self.main_base, self.main_max = \
                    (int(num, 16) for num in line['payload'].replace(" -","")[:-2].split(" ")[2:4])

    def add_breakpoint(
        self,
        bkpt: Breakpoint,
    ):
        """Activate breakpoint

        Args:
            bkpt (Breakpoint): Breakpoint object to activate
        """
        bkpt.bkpt_no = self.bkpt_no
        self.active_breakpoints.append(bkpt)
        if isinstance(bkpt, WatchPoint):
            self.write(f"{bkpt.watch_type} * 0x{bkpt.address:X}")
        else:
            self.write(f"b * 0x{self.main_base + (bkpt.address & 0xFFFFFFFF):X}")
        if not bkpt.active:
            self.write(f"disable {bkpt.bkpt_no}")
        self.bkpt_no += 1

    def wait_for_break(
        self,
        timeout: float = 60.0,
    ):
        """
        Wait for and deal with a breakpoint being hit

        Args:
            timeout (float, optional): Time in seconds to wait before timing out. Defaults to 60.0
        """
        response = self.get_gdb_response(timeout_sec = timeout, raise_error_on_timeout = False)
        if response is not None:
            bkpt_hit: Breakpoint = None
            for line in response:
                if line['message'] == "breakpoint-modified":
                    bkpt_info = line['payload']['bkpt']
                    bkpt_no = int(bkpt_info['number'])
                    bkpt_hit = self.active_breakpoints[bkpt_no - 1]
                    break
            if bkpt_hit is not None:
                print(f"Breakpoint at \"{bkpt_hit.name}\" hit")
                if isinstance(bkpt_hit, WatchPoint):
                    access_address: int = None
                    for line in reversed(response):
                        if "frame" in line['payload']:
                            access_address = int(line['payload']['frame']['addr'],16)
                            break
                    access_address = 0x7100000000 | (access_address - self.main_base)
                    print(f"Access address: {access_address:X}")
                self.clear_responses()
                if bkpt_hit.on_break is not None:
                    bkpt_hit.on_break(self, bkpt_hit)
                self.resume_execution()
                self.wait_for_break()

    def wait_for_response(
        self,
        target_type: Optional[str] = "console",
    ) -> List[dict]:
        """Wait until response from gdb of type target_type

        Args:
            target_type (Optional[str], optional): mi3 type to wait for. Defaults to "console".

        Returns:
            List[dict]: First mi3 response line of type target_type
        """
        found = False
        while not found:
            response = self.get_gdb_response()
            for line in response:
                if line['type'] == target_type:
                    found = True
                    break
        return response

    def log_response(
        self,
        response: List[dict],
        detailed: Optional[bool] = False,
    ):
        """Log a mi3 response List[dict]

        Args:
            response (List[dict]): mi3 response to log
            detailed (bool, optional): Whether or not to log full response. Defaults to False
        """
        if detailed:
            print(response)
        else:
            for line in self.extract_payloads(self.filter_response(response)):
                print(line)

    @staticmethod
    def filter_response(
        response: List[dict],
        target_type: Optional[str] = "console",
    ) -> List[dict]:
        """
        Filter mi3 response down to only that of target_type

        Args:
            response (List[dict]): mi3 response to filter
            target_type (Optional[str], optional): mi3 type to filter for. Defaults to "console"

        Returns:
            List[dict]: Filtered mi3 response
        """
        return [line for line in response if line['type'] == target_type]

    @staticmethod
    def extract_payloads(
        response: List[dict],
    ) -> List[str]:
        """Extract only the payloads of a mi3 response

        Args:
            response (List[dict]): mi3 response to extract from

        Returns:
            List[str]: Extracted payloads
        """
        return [line["payload"] for line in response if line["payload"] != ""]
