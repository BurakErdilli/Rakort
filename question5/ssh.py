import paramiko
import threading
import ipaddress


class SSHManager:
    def __init__(self, network_block, username, password):
        """Initialize the SSHManager with a network block and credentials."""
        self.network_block = ipaddress.ip_network(network_block)
        self.username = username
        self.password = password

    def execute_command(self, ip, command):
        """Establish an SSH connection to the given IP and execute a command."""
        try:
            # Create SSH client
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect to the server
            client.connect(str(ip), username=self.username,
                           password=self.password)
            print(f"Connected to {ip}")

            # Execute the command
            stdin, stdout, stderr = client.exec_command(command)
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')

            # Close the connection
            client.close()

            # Print output and error
            print(f"Output from {ip}:\n{output}")
            if error:
                print(f"Error from {ip}:\n{error}")

        except Exception as e:
            print(f"Failed to connect to {ip}: {str(e)}")

    def run_commands(self, command):
        """Run a command on all hosts in the network block simultaneously."""
        threads = []
        for ip in self.network_block.hosts():  # Iterate through all hosts in the network block
            thread = threading.Thread(
                target=self.execute_command, args=(ip, command))
            threads.append(thread)
            thread.start()  # Start the thread

        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        print("All commands executed.")


if __name__ == "__main__":
    # Example usage
    network_block = "192.168.1.0/24"  # Replace with your network block
    username = "your_username"  # Replace with your SSH username
    password = "your_password"  # Replace with your SSH password
    command = "uptime"  # Replace with the command you want to execute

    ssh_manager = SSHManager(network_block, username, password)
    ssh_manager.run_commands(command)
