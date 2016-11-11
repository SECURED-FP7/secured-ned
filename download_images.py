import os
import json
import psar
import ConfigParser
GRAPH_LOCATION='TVDM/userGraph/'
IMAGES_LOCATION='/var/lib/libvirt/images/'

for filename in os.listdir(GRAPH_LOCATION):
	
	with open(GRAPH_LOCATION+filename,'rb') as file:
		print filename
		try:
			user=json.load(file)
		except:
			pass
		
		else:
			if 'PSASet' in user:
				for psa in user['PSASet']:
					id=psa['id']
					disk=psa['security_controls'][0]['imgName']
					print id + ' ' +disk

					try:
						with open(IMAGES_LOCATION+disk,'rb'):
							pass
					except:

						conf=ConfigParser.ConfigParser()
						conf.read('psar.conf')
						PSAR_URL=os.getenv('PSAR_URL',conf.get('PSAR','schema')+'://'+conf.get('PSAR','ip_address')+':'+conf.get('PSAR','port'))
					

						psar_client=psar.Client(PSAR_URL)
						
						try:
				
							if conf.get('PSAR','auth')=='off':
								psar_client.get_image_file(id,IMAGES_LOCATION+disk)	
							elif conf.get('PSAR','auth')=='on':
								token=psar_client.get_token(user=conf.get('PSAR','user'),
								password=conf.get('PSAR','password'), 
								tenant=conf.get('PSAR','tenant'),auth_URL=conf.get('PSAR','auth_url'))
							
								psar_client.get_image_file(id,IMAGES_LOCATION+disk,token=token)	

     						except NoOptionError:
							psar_client.get_image_file(id,IMAGES_LOCATION+disk)
