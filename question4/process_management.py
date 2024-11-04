import time
import random
from multiprocessing import Process
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import func

# Database connection
DATABASE_URL = "sqlite:///process_states.db"
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Define the ProcessState model


class ProcessState(Base):
    __tablename__ = 'process_states'

    id = Column(Integer, primary_key=True)
    process_id = Column(Integer)
    status = Column(String)
    start_time = Column(DateTime, server_default=func.now())
    end_time = Column(DateTime)


# Create tables in the database
Base.metadata.create_all(engine)


def process_task(process_id):
    """Simulate a task performed by a process."""
    start_time = time.time()
    time.sleep(random.uniform(0.1, 2.0))  # Simulate work by sleeping

    # Update the database with the process status
    session = Session()
    session.add(ProcessState(process_id=process_id,
                status='Completed', end_time=func.now()))
    session.commit()
    session.close()

    print(
        f"Process {process_id} completed in {time.time() - start_time:.2f} seconds.")


def run_processes(num_processes=1000):
    """Start the specified number of processes."""
    processes = []

    for i in range(num_processes):
        p = Process(target=process_task, args=(i,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()  # Wait for all processes to finish

    print("All processes have completed.")


def fetch_process_states():
    """Fetch and print all process states from the database."""
    session = Session()
    states = session.query(ProcessState).all()

    # Print all process states
    for state in states:
        print(
            f'Process ID: {state.process_id}, Status: {state.status}, Start Time: {state.start_time}, End Time: {state.end_time}')

    session.close()


def fetch_remaining_processes(num_processes):
    """Fetch and print remaining processes that are not completed."""
    session = Session()
    remaining_processes = session.query(ProcessState).filter(
        ProcessState.status != 'Completed').all()

    print("\nRemaining Processes:")
    for process in remaining_processes:
        print(
            f'Process ID: {process.process_id}, Status: {process.status}, Start Time: {process.start_time}, End Time: {process.end_time}')

    session.close()


if __name__ == "__main__":
    start_time = time.time()
    run_processes()
    fetch_process_states()  # Fetch and print the process states
    fetch_remaining_processes(1000)  # Check for remaining processes
    print(
        f"Total time for all processes: {time.time() - start_time:.2f} seconds.")
