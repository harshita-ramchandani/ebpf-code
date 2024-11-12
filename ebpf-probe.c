int kprobe__sys_clone(void *ctx){
	bpf_trace_printk("hello world\n");
	return 0;
}
