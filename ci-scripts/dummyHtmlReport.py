#/*
# * Licensed to the OpenAirInterface (OAI) Software Alliance under one or more
# * contributor license agreements.  See the NOTICE file distributed with
# * this work for additional information regarding copyright ownership.
# * The OpenAirInterface Software Alliance licenses this file to You under
# * the OAI Public License, Version 1.1  (the "License"); you may not use this file
# * except in compliance with the License.
# * You may obtain a copy of the License at
# *
# *   http://www.openairinterface.org/?page_id=698
# *
# * Unless required by applicable law or agreed to in writing, software
# * distributed under the License is distributed on an "AS IS" BASIS,
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# * See the License for the specific language governing permissions and
# * limitations under the License.
# *-------------------------------------------------------------------------------
# * For more information about the OpenAirInterface (OAI) Software Alliance:
# *   contact@openairinterface.org
# */
#---------------------------------------------------------------------

import os
import re
import sys
import subprocess
import yaml
import argparse


class HtmlReport():
	def __init__(self):
		self.job_name = ''
		self.job_id = ''
		self.job_url = ''
		self.job_start_time = 'TEMPLATE_TIME'
		self.file_name = ''

	def _parse_args(self) -> argparse.Namespace:
		"""Parse the command line args

		Returns:
			argparse.Namespace: the created parser
		"""
		parser = argparse.ArgumentParser(description='OAI HTML Report Generation for CI')

		# Jenkins Job name
		parser.add_argument(
			'--job_name',
			action='store',
			required=True,
			help='Jenkins Job name',
		)
		# Jenkins Job Build ID
		parser.add_argument(
			'--job_id',
			action='store',
			required=True,
			help='Jenkins Job Build ID',
		)
		# Jenkins Job Build URL
		parser.add_argument(
			'--job_url',
			action='store',
			required=True,
			help='Jenkins Job Build URL',
		)
		return parser.parse_args()

	def generate(self):
		cwd = os.getcwd()
		if re.search('OAI-CN5G-FED-OC', self.job_name) is not None:
			self.file_name = '/test_results_oai_cn5g_oc_dummy.html'
		self.file = open(cwd + f'{self.file_name}', 'w')
		self.generateHeader()
		self.generateFooter()
		self.file.close()

		sys.exit(0)

	def generateHeader(self):
		# HTML Header
		self.file.write('<!DOCTYPE html>\n')
		self.file.write('<html class="no-js" lang="en-US">\n')
		self.file.write('<head>\n')
		self.file.write('  <meta name="viewport" content="width=device-width, initial-scale=1">\n')
		self.file.write('  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">\n')
		self.file.write('  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>\n')
		self.file.write('  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>\n')
		self.file.write('  <title>OAI 5G Core Network Test Results for ' + self.job_name + ' job build #' + self.job_id + '</title>\n')
		self.file.write('</head>\n')
		self.file.write('<body><div class="container">\n')
		self.file.write('  <table width = "100%" style="border-collapse: collapse; border: none;">\n')
		self.file.write('   <tr style="border-collapse: collapse; border: none;">\n')
		self.file.write('   <td style="border-collapse: collapse; border: none;">\n')
		self.file.write('    <a href="http://www.openairinterface.org/">\n')
		self.file.write('      <img src="http://www.openairinterface.org/wp-content/uploads/2016/03/cropped-oai_final_logo2.png" alt="" border="none" height=50 width=150>\n')
		self.file.write('      </img>\n')
		self.file.write('    </a>\n')
		self.file.write('   </td>\n')
		self.file.write('   <td style="border-collapse: collapse; border: none; vertical-align: center;">\n')
		self.file.write('     <b><font size = "6">Job Summary -- Job: ' + self.job_name + ' -- Build-ID: <a href="' + self.job_url + '">' + self.job_id + '</a></font></b>\n')
		self.file.write('   </td>\n')
		self.file.write('   </tr>\n')
		self.file.write('  </table>\n')
		self.file.write('  <br>\n')
		self.file.write('  <div class="alert alert-warning">\n')
		self.file.write('    <strong>NO TESTING DONE BEFORE MIGRATION TO NEW RAN EMULATOR <span class="glyphicon glyphicon-warning-sign"></span></strong>\n')
		self.file.write('  </div>\n')	

	def generateFooter(self):
		self.file.write('  <div class="well well-lg">End of Test Report -- Copyright <span class="glyphicon glyphicon-copyright-mark"></span> 2020 <a href="http://www.openairinterface.org/">OpenAirInterface</a>. All Rights Reserved.</div>\n')
		self.file.write('</div></body>\n')
		self.file.write('</html>\n')

#--------------------------------------------------------------------------------------------------------
#
# Start of main
#
#--------------------------------------------------------------------------------------------------------

HTML = HtmlReport()
args = HTML._parse_args()

HTML.job_name = args.job_name
HTML.job_id = args.job_id
HTML.job_url = args.job_url
HTML.file_name = '/test_results_oai_cn5g_dummy.html'
HTML.generate()
