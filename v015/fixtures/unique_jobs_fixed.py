def unique_jobs(jobs):
    seen, result = set(), []
    for job in jobs:
        if job not in seen:
            seen.add(job)
            result.append(job)
    return result
