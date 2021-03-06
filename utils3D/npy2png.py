import argparse, os
import numpy as np
import visdom
from visualize import plot_voxel, plot_colored_voxel
from multiprocessing import Process

import pdb

def parse_opts():
	desc = "visualize npy voxels of prob to visdom"
	parser = argparse.ArgumentParser(description=desc)

	parser.add_argument('--dir_npy', type=str, default='', help='directory that contains npy files')
	parser.add_argument('--dir_dest', type=str, default='', help='directory to put result png files')
	parser.add_argument('--batch_size', type=int, default=64, help='The size of batch')
	parser.add_argument('--epoch_from', type=int, default=0, help='epoch to start plotting from')
	parser.add_argument('--epoch_to', type=int, default=-1, help='epoch to end plotting')
	parser.add_argument('--epoch_every', type=int, default=1, help='plot every N epochs')
	parser.add_argument('--fname', type=str, default='', help='single file to visualize')
	parser.add_argument('--port', type=int, default='8097', help='port to use')
 
	return check_opts(parser.parse_args())

"""checking arguments"""
def check_opts(opts):
	return opts

def main():

	opts = parse_opts()
	if opts is None:
		exit()
	
	if len(opts.fname)==0 and len(opts.dir_npy)==0:
		print( 'Target is not provided' )
		exit()

	if len(opts.dir_npy) == 0:
		opts.dir_npy = os.path.dirname( opts.fname )

	if len(opts.dir_dest) == 0:
		opts.dir_dest = os.path.join( opts.dir_npy, 'png' )

	if not os.path.exists( opts.dir_dest ):
		os.makedirs( opts.dir_dest )
	
	if len(opts.fname)>0:
		fnames = [opts.fname]
		try:
			opts.epoch_to = int(opts.fname[-12:-9])
		except:
			print('ignoring epoch...'+opts.fname)
	else:
		fnames = [os.path.join(dirpath,f) \
					for dirpath, dirnames, files in os.walk(opts.dir_npy)
							for f in files if f.endswith('.npy') ]
		fnames.sort()

	for iF in range(len(fnames)//opts.epoch_every):
		fname = fnames[iF*opts.epoch_every]
		print( 'loading from {}'.format(fname) )
		try:
			epoch = int(fname[-12:-9])
			if epoch < opts.epoch_from or opts.epoch_to < epoch:
				continue
		except:
			print('ignoring epoch...'+fname)
			epoch=os.path.basename(fname)[:-4]

		g_objects = np.load(fname)
	
		if g_objects.ndim == 4:
			for i in range(g_objects.shape[0]):
				if g_objects[i].max() > 0.5:
					print( 'plotting epoch {} sample {}...'.format(epoch, i) )
					plot_voxel(np.squeeze(g_objects[i]>0.5), os.path.join(opts.dir_dest,'_'.join(map(str,[epoch,i]))))
				else:
					print( 'max={}'.format(g_objects[i].max()) )
		elif g_objects.ndim == 5:
			for i in range(g_objects.shape[0]):
				if g_objects[i,0].max() > 0.5:
					print( 'plotting epoch {} sample {}...'.format(epoch, i) )
					plot_colored_voxel(np.squeeze(g_objects[i,0]>0.5),g_objects[i,1:4],
								os.path.join(opts.dir_dest,'_'.join(map(str,[epoch,i]))))
				else:
					print( 'max={}'.format(g_objects[i].max()) )
	

if __name__ == '__main__':
	main()
