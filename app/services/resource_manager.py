# In app/services/resource_manager.py

import threading

class ResourceManager:
    def __init__(self, total_cpu: int, total_memory_mb: int):
        self.total_cpu = total_cpu
        self.total_memory = total_memory_mb
        self.used_cpu = 0
        self.used_memory = 0
        # A lock is crucial to prevent race conditions if we ever have multiple workers
        self._lock = threading.Lock()

    def can_allocate(self, cpu_req: int, mem_req: int) -> bool:
        """Checks if resources can be allocated without acquiring them."""
        return (self.used_cpu + cpu_req <= self.total_cpu and
                self.used_memory + mem_req <= self.total_memory)

    def allocate(self, cpu_req: int, mem_req: int) -> bool:
        """Tries to allocate resources. Returns True if successful, False otherwise."""
        with self._lock:
            if self.can_allocate(cpu_req, mem_req):
                self.used_cpu += cpu_req
                self.used_memory += mem_req
                print(f"RESOURCE_MANAGER: Allocated {cpu_req} CPU, {mem_req}MB. Usage is now {self.used_cpu}/{self.total_cpu} CPU, {self.used_memory}/{self.total_memory}MB.")
                return True
            return False

    def release(self, cpu_req: int, mem_req: int):
        """Releases allocated resources."""
        with self._lock:
            self.used_cpu -= cpu_req
            self.used_memory -= mem_req
            print(f"RESOURCE_MANAGER: Released {cpu_req} CPU, {mem_req}MB. Usage is now {self.used_cpu}/{self.total_cpu} CPU, {self.used_memory}/{self.total_memory}MB.")

# Create a single instance based on the Test Scenario 4 constraints [cite: 224]
# System has 8 CPU units and 4096 MB memory total
resource_manager = ResourceManager(total_cpu=8, total_memory_mb=4096)