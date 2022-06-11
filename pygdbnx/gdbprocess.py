"""Wrapper around pygdbmi.GdbController for easier switch connection"""

from typing import Optional,List
import pygdbmi.gdbcontroller
import pygdbmi.constants

from .breakpoint import Breakpoint


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
            ip_address (str): Local IP address of the nintendo switch console

            breakpoints (Optional[List[Breakpoint]], optional): List of breakpoints
            to apply on start of process

            path_to_gdb (Optional[str], optional): Path to gdb executable to run.
            Defaults to "aarch64-none-elf-gdb.exe".

            time_to_check_for_additional_output_sec (float, optional): When parsing responses,
            wait this amout of time before exiting (exits before timeout is reached to save time).
            If <= 0, full timeout time is used.
            Defaults to pygdbmi.constants.DEFAULT_TIME_TO_CHECK_FOR_ADDITIONAL_OUTPUT_SEC.
        """
        super().__init__([path_to_gdb,"--interpreter=mi3"], time_to_check_for_additional_output_sec)
        self.ip_address = ip_address
        self.active_breakpoints = {}
        self.main_base: int = None
        self.heap_base: int = None
        self.clear_responses()
        self.connect()

    def clear_responses(
        self,
    ):
        """
        Clear all cached gdb responses by sending an empty string
        """
        self.write("")

    def connect(
        self,
    ):
        """
        Connect to the switch with the ip address stored in self.ip_address
        """
        self.write(f"target extended-remote {self.ip_address}:22225", read_response=False)
        self.log_response(self.wait_for_response())

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
            detailed (bool, optional): Whether or not to log full response. Defaults to False.
        """
        if detailed:
            print(response)
        else:
            for line in self.extract_payloads(response):
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
            target_type (Optional[str], optional): mi3 type to filter for. Defaults to "console".

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
