import os
import logging
import threading

import boto

try:
	import RPi.GPIO as GPIO
except ImportError:
	GPIO = None

class App(object):
	def __init__(self, pid, pid_timeout = 5, bounce_timeout = 200):
		self.log = logging.getLogger(self.__module__)

		self.stdin_path = '/dev/null'
		self.stdout_path = '/dev/null'
		self.stderr_path = '/dev/null'
		self.pidfile_path =  os.path.join('/var/run/', pid)
		self.pidfile_timeout = pid_timeout

		self.status = 0
		self.bounce_timeout = bounce_timeout

	def run(self):
		self.log.info("Starting")
		try:
			self._run()
		except Exception as ex:
			self.log.exception(ex)
		self.log.info("Shutting down")

	def _pin(self, pin, value):
		self._set_pin(value) if value else self._clear_pin(value)

	def _set_pin(self, pin):
		self.status = (1 << pin) | self.status
		self.log.debug("Set pin: %d" % pin)

	def _clear_pin(self, pin):
		self.status = ~(1 << pin) & self.status
		self.log.debug("Cleared pin: %d" % pin)

	def _run(self):
		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BOARD)

		# Configure input pins
		for pin in [0, 1, 2]:
			GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

			self._pin(pin, GPIO.input(pin))

			GPIO.add_event_detect(pin, GPIO.RISING, bouncetime=self.bounce_timeout, callback=self._set_pin)
			GPIO.add_event_detect(pin, GPIO.FALLING, bouncetime=self.bounce_timeout, callback=self._clear_pin)

		# Set the relay output
		GPIO.setup(3, GPIO.OUT)
		GPIO.output(3, False)