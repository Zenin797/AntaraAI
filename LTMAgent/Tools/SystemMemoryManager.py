import psutil

def get_memory_usage():
    """
    Returns the current system memory usage as a percentage.
    
    Returns:
        float: Percentage of memory currently in use.
    """
    return psutil.virtual_memory().percent

if __name__ == "__main__":
    usage = get_memory_usage()
    print(f"Memory usage: {usage}%")