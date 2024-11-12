from bcc import BPF
from time import sleep

# Manually define the performance event types and event configuration constants
PERF_TYPE_HARDWARE = 0  # Constant for hardware events
PERF_COUNT_HW_INSTRUCTIONS = 0x00  # Hardware event type for instructions
PERF_COUNT_HW_CPU_CYCLES = 0x01  # Hardware event type for CPU cycles
PERF_COUNT_HW_CACHE_MISSES = 0x08  # Hardware event type for cache misses
PERF_TYPE_SOFTWARE = 1  # Constant for software events
PERF_COUNT_SW_PAGE_FAULTS = 0x06  # Software event type for page faults

# Set the PID of the process to monitor
TARGET_PID = 93505  # Replace this with your actual target PID

# Define eBPF program
bpf_program = """
#include <uapi/linux/ptrace.h>
#include <linux/perf_event.h>

BPF_ARRAY(instructions, u64, 1);
BPF_ARRAY(cycles, u64, 1);
BPF_ARRAY(cache_misses, u64, 1);
BPF_ARRAY(page_faults, u64, 1);

int count_events(struct pt_regs *ctx) {
    u32 index = 0;

    u64 inst = bpf_perf_event_read(&instructions, index);
    u64 cyc = bpf_perf_event_read(&cycles, index);
    u64 cache = bpf_perf_event_read(&cache_misses, index);
    u64 faults = bpf_perf_event_read(&page_faults, index);

    return 0;
}
"""

# Load and attach the BPF program
b = BPF(text=bpf_program)

# Attach performance events using manually defined constants
b.attach_perf_event(ev_type=PERF_TYPE_HARDWARE, ev_config=PERF_COUNT_HW_INSTRUCTIONS, fn_name="count_events", pid=TARGET_PID)
b.attach_perf_event(ev_type=PERF_TYPE_HARDWARE, ev_config=PERF_COUNT_HW_CPU_CYCLES, fn_name="count_events", pid=TARGET_PID)
b.attach_perf_event(ev_type=PERF_TYPE_HARDWARE, ev_config=PERF_COUNT_HW_CACHE_MISSES, fn_name="count_events", pid=TARGET_PID)
b.attach_perf_event(ev_type=PERF_TYPE_SOFTWARE, ev_config=PERF_COUNT_SW_PAGE_FAULTS, fn_name="count_events", pid=TARGET_PID)

print("Tracking performance metrics for PID:", TARGET_PID)

# Main loop to print metrics
try:
    while True:
        sleep(1)
        instructions = b["instructions"][0].value
        cycles = b["cycles"][0].value
        cache_misses = b["cache_misses"][0].value
        page_faults = b["page_faults"][0].value

        print("\nPerformance Metrics:")
        print("Instructions:", instructions)
        print("Cycles:", cycles)
        print("Cache Misses:", cache_misses)
        print("Page Faults:", page_faults)

        if cycles > 0 and instructions > 0:
            cpi = cycles / instructions
            print("CPI:", cpi)
        else:
            print("CPI: Unable to calculate (instructions or cycles missing)")

except KeyboardInterrupt:
    print("Exiting...")
finally:
    # Detach performance events
    b.detach_perf_event(ev_type=PERF_TYPE_HARDWARE, ev_config=PERF_COUNT_HW_INSTRUCTIONS)
    b.detach_perf_event(ev_type=PERF_TYPE_HARDWARE, ev_config=PERF_COUNT_HW_CPU_CYCLES)
    b.detach_perf_event(ev_type=PERF_TYPE_HARDWARE, ev_config=PERF_COUNT_HW_CACHE_MISSES)
    b.detach_perf_event(ev_type=PERF_TYPE_SOFTWARE, ev_config=PERF_COUNT_SW_PAGE_FAULTS)
