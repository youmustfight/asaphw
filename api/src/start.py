from api.api import start_api

# For any services I code, I always have a start file
# That way we can tweak what/how startup happens w/ env flags
# Ex: api vs. worker vs. cron
if __name__ == "__main__":
    start_api()