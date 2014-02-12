#!/usr/bin/python
# -*- coding: cp1252 -*-
#    Copyright 2014, Chaz Littlejohn 
#                    _   _                          _   _           _ _ 
#                   | | | |                        | | (_)         | | |
#    _ __ ___   __ _| |_| |__   ___ _ __ ___   __ _| |_ _  ___ __ _| | |
#   | '_ ` _ \ / _` | __| '_ \ / _ \ '_ ` _ \ / _` | __| |/ __/ _` | | |
#   | | | | | | (_| | |_| | | |  __/ | | | | | (_| | |_| | (_| (_| | |_|
#   |_| |_| |_|\__,_|\__|_| |_|\___|_| |_| |_|\__,_|\__|_|\___\__,_|_(_)
#                                                                 
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#    
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

#########################################################################

import os
import re
import shutil
import episodes
import difflib
import sys

#Adventure Time - s02e02b - Blood Under the Skin {C_P} (720p).mkv
#Adventure Time - s03e02a - Memory of a Memory.mkv
#Adventure Time - s04e03a - Return To The Nightosphere (1).mp4
re_adventure_time = re.compile("Adventure\sTime\s\-\ss\d+e\d+[ab]?(\s\-)?\s(?P<TITLE>[^{\.\(]+?)(\s{C_P}\s\(720p\))?(\(\d\))?\.")

def checklists(item1, item2):
	for w1 in [l for l in item1.split() if l!='and']:
		for w2 in [l for l in item2.split() if l!='and']:
			if difflib.SequenceMatcher(a=w1, b=w2).ratio() >= 0.9:
				return True
	if item1.replace(' ','')==item2.replace(' ', ''):
		return True
	return False

def episode_data(data={}):
	for title, season, episode in episodes.listing:
		scrubbed = title.replace('?', '').replace(":", "")
		data[scrubbed] = {'season':season, 'episode':episode, 'title':scrubbed}
	print "Read %d of %d episodes from the listing" % (len(episodes.listing),len(data))
	return data
		
def sorted_videos(directory, videos=[]):
	for root, dirs, files in os.walk(directory, topdown=False):
		for name in files:
			if name.endswith('.avi') or name.endswith('.mkv') or name.endswith('.mp4'):
				videos.append(name)
	videos.sort()
	return videos

def matching_video(data, videos, assigned=[]):
	for name in videos:	
		match = None
		m2 = re_adventure_time.search(name)
		if m2: 
			match = data.get(m2.group("TITLE"))
			if not match:
				for title, info in data.iteritems():
					if (checklists(m2.group("TITLE"),info['title']) and 
						info['title'] not in assigned):
						match = info
						break
		if match:
			match['name'] = name
			assigned.append(match['title'])
			yield match, assigned
		else:
			print 'Could not match file', name
			
def organize_files(data, videos, directory):
	for match, assigned in matching_video(data, videos):
		filename = "Adventure Time - s%se%s - %s%s" % (match['season'], match['episode'], match['title'], os.path.splitext(match['name'])[1])
		folder = os.path.join(directory,'Season %s' % match['season'])
		if not os.path.exists(folder):
			os.mkdir(folder)
		if os.path.exists(os.path.join(directory,match['name'])):
			shutil.move(os.path.join(directory,match['name']),os.path.join(directory,folder,filename))
	print "Matched %d of %d video files in %s" % (len(assigned), len(videos), directory)
			
			
def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
		
	directory = argv[0]
	data = episode_data()
	videos = sorted_videos(directory)
	organize_files(data, videos, directory)

if __name__ == '__main__':
    sys.exit(main())
			
