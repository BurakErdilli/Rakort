import paramiko
import time
import re


class DHCPParser:
    def __init__(self, host, username, password, command, duration=300):
        """
        Initialize the DHCPParser with server connection details and command.

        :param host: The server's IP address.
        :param username: The username for SSH connection.
        :param password: The password for SSH connection.
        :param command: The command to be executed on the server.
        :param duration: The duration for which to run the command (in seconds).
        """
        self.host = host
        self.username = username
        self.password = password
        self.command = command
        self.duration = duration
        self.results = []

    def connect_ssh(self):
        """Establish an SSH connection to the server."""
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(self.host, username=self.username,
                             password=self.password)
            print("SSH connection established.")
        except Exception as e:
            print(f"An error occurred while establishing SSH connection: {e}")

    def run_command(self):
        """Run the specified command and collect data for a given duration."""
        self.connect_ssh()
        stdin, stdout, stderr = self.ssh.exec_command(self.command)

        # Start time to keep track of duration
        start_time = time.time()

        while time.time() - start_time < self.duration:
            line = stdout.readline()
            if line:
                self.parse_line(line)

        self.ssh.close()

    def parse_line(self, line):
        """Parse each line for DHCP messages."""
        # Regular expression to match the required DHCP fields
        dhcp_request_pattern = re.compile(
            r'OPTION: 53 \( 1\) DHCP message type 3 \(DHCPREQUEST\)')
        client_id_pattern = re.compile(
            r'OPTION: 61 \( 7\) Client-identifier (.+)')
        request_ip_pattern = re.compile(
            r'OPTION: 50 \( 4\) Request IP address (.+)')
        vendor_class_pattern = re.compile(
            r'OPTION: 60 \( 15\) Vendor class identifier (.+)')
        host_name_pattern = re.compile(r'OPTION: 12 \( 12\) Host name (.+)')

        # Check if the line contains a DHCP request
        if dhcp_request_pattern.search(line):
            client_id = client_id_pattern.search(line)
            request_ip = request_ip_pattern.search(line)
            vendor_class = vendor_class_pattern.search(line)
            host_name = host_name_pattern.search(line)

            # Store parsed data in a dictionary
            data = {
                "Client-identifier": client_id.group(1) if client_id else None,
                "Request IP address": request_ip.group(1) if request_ip else None,
                "Vendor class identifier": vendor_class.group(1) if vendor_class else None,
                "Host name": host_name.group(1) if host_name else None
            }

            self.results.append(data)
            print(f"Parsed data: {data}")

    def save_results(self, filename):
        """Save parsed results to a text file."""
        with open(filename, 'w') as file:
            for result in self.results:
                file.write(f"{result}\n")
        print(f"Parsed data saved to {filename}.")


if __name__ == "__main__":
    # Define parameters
    HOST = 'your_server_ip'  # Enter the server's IP address
    USERNAME = 'your_username'  # Enter your username
    PASSWORD = 'your_password'  # Enter your password
    COMMAND = 'your_command'  # Enter the SSH command you want to monitor
    DURATION = 300  # Listening duration (in seconds)

    parser = DHCPParser(HOST, USERNAME, PASSWORD, COMMAND, DURATION)
    parser.run_command()
    parser.save_results('parsed_dhcp_requests.txt')
