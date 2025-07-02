def my_rq_exception_handler(job, exc_type, exc_value, traceback):
    print(f"Exception in job {job.id}: {exc_type.__name__}: {exc_value}")