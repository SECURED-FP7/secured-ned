#!/usr/bin/python

from requests import get, put, delete, patch, post
import urllib
from keystoneclient.v2_0 import client
import argparse,json

'''
Client for the PSAR API. All methods return a Response object.

TO-DO: Currently only tested without authentication. 
'''

	
class Client:
	def __init__(self,base_url):
		self.base_url=base_url+'/v1/'
	
	
	def get_token(self,user,password,tenant,auth_URL):
		keystone = client.Client(username=user, password=password, tenant_name=tenant, auth_url=auth_URL)
		return keystone.get_raw_token_from_identity_service(auth_url=auth_URL,username=user, password=password,tenant_name=tenant).auth_token
	
	def add_token_param(self,token,first_param): #TO-DO:Change authentication so that it goes on the header instead of url
		return ('?' if first_param else '&')+urllib.urlencode({'auth_token':token})
	
	#Status
	
	
	def get_status(self,token=None):
		
		url = self.base_url+'status'
		if token:
			url += add_token_param(token=token,first_param=True)
		return get(url)
		
	#PSA
		
	def create_psa(self,name=None,token=None):
		url = self.base_url+'PSA/images/'
		if token:
	                url +=add_token_param(token=token,first_param=True)
		if name:
				url += '&name='+name
		return post(url)
		
	def delete_psa(self,psa_id,token=None):
		url = self.base_url+'PSA/images/'+psa_id+'/'
		if token:
			url +=add_token_param(token=token,first_param=True)
		return delete(url)		
	
	def get_image_list(self, id=None,token=None):
		url = self.base_url+'PSA/images/'
		if id:
			url += '?id='+id
		if token:
			url += add_token_param(token=token,first_param=not id)
		return get(url)
	
	
	
	#Manifest
	
	
	
	def get_manifest(self, psa_id,path,token=None):
		url = self.base_url+'PSA/manifest/'+psa_id
		if token:
			url += self.add_token_param(token=token,first_param=True)
		r=get(url)
		if r.status_code == 200:
                	with open(path, 'wb') as f:
                        	for chunk in r.iter_content(chunk_size=1024):
                                	f.write(chunk)
                return r

	
	def delete_manifest (self,psa_id,token=None):
		url = self.base_url+'PSA/manifest/'+psa_id+'/file'
		if token:
			url += add_token_param(token=token,first_param=True)
		return delete(url)
	
	def put_manifest_file(self,psa_id,path,token=None):
		with open(path,'rb') as f:
			url=self.base_url+'PSA/manifest/'+str(psa_id)+'/file'
			if token:
				url += add_token_param(token=token,first_param=True)
			files={'file':f}
			return put(url,files=files)
	
	
	
	
	#Images
	
	
	def get_image_file(self,psa_id, path,token=None):
		url = self.base_url+'PSA/images/'+psa_id+'/file'
		if token:
			url += add_token_param(token=token,first_param=True)
		r=get(url)
		if r.status_code == 200:
			with open(path, 'wb') as f:
				for chunk in r.iter_content(chunk_size=1024):
					f.write(chunk)
		return r

	def put_image_file(self, psa_id, path, disk_format, container_format,token=None):
		url=self.base_url+'PSA/images/'+psa_id+'/file?'+urllib.urlencode({"disk_format":disk_format,'container_format':container_format})

		if token:
			url += add_token_param(token=token,first_param=False)
				
		with open (path, 'rb') as f:
			files={'file':f}
			headers={'Content-Type':'application/octet-stream','Content-Disposition':'attachment; filename='+psa_id}
			return put(url,data=f,headers=headers)
			#return put(url,files=files,headers=headers)
	
	def put_image(self,psa_id,name=None,token=None):
		url = self.base_url+'PSA/images/'+psa_id+'/'
		if token:
	            url += add_token_param(token=token,first_param=True)
		if name:
			url += '&name='+name	
		return put(url)
	
	def delete_image(self, psa_id,token=None):
		url = self.base_url+'PSA/images/'+psa_id+'/file'
		if token:
			url += add_token_param(token=token,first_param=True)
		return delete(url)
	
	def get_image_location (self,psa_id,token=None):
		url = self.base_url+'PSA/images/'+psa_id+'/image_location'
		if token:
			url += add_token_param(token=token,first_param=True)
		return get(url)	

	def patch_image(self, psa_id, new_status,token=None):
		url = self.base_url+'PSA/images/'+psa_id+'/?status='+new_status
		if token:
			url += add_token_param(token=token,first_param=False)
		return patch(url)

	#Plugin

	def get_plugin_file(self,psa_id,path,token=None):
		url =self.base_url+'PSA/M2Lplugins/'+psa_id+'/'
		if token:
			url += add_token_param(token=token,first_param=True)
		r=get(url)
		if r.status_code == 200:
			with open(path, 'wb') as f:
				for chunk in r.iter_content(chunk_size=1024):
					f.write(chunk)
		return r

	def put_plugin_file(self,psa_id,path,token=None):
		url=self.base_url+'PSA/M2Lplugins/'+psa_id+'/file'
		if token:
			url += add_token_param(token=token,first_param=True)
		with open(path,'rb') as f:
			files={'file':f}
			return put(url,files=files)
	def put_plugin(self, psa_id,name=None,new_url=None,token=None):
		url=self.base_url+'PSA/M2Lplugins/'+psa_id+'/'
		if name: 
			url += '?name='+name
		if token:
			url += add_token_param(token=token,first_param=not(name))
		if new_url:
			url+='&url='+new_url
	def delete_plugin(self, psa_id,token=None):
		url = self.base_url+'PSA/M2Lplugins/'+psa_id+'/file'
		if token:
			url += add_token_param(token=token,first_param=True)
		return delete(url)
	
	def get_plugin_location (self, psa_id,token=None):
		url = self.base_url+'PSA/M2Lplugins/'+psa_id+'/plugin_location'
		if token:
			url += add_token_param(token=token,first_param=True)
		return get(url)

		

	

	#PSARL
			
	
	def put_psarl_location(self, psarl_id,new_location,token=None):
		url = self.base_url+'PSARLs/'+psarl_id+'/?location='+new_location
		if token:
			url += add_token_param(token=token,first_param=False)
		
		return put(url)





if __name__=='__main__':
	#TO-DO: Take arguments (such as the url of the psar) from environment
	#Functions
	PSAR_URL='http://195.235.93.146:8080'

	def list_psa(args):
		if args.url:
			c=Client(args.url)
		else:
			 c=Client(PSAR_URL)
		if args.id:
			r=c.get_image_list(token=args.token)
		else:
			r=c.get_image_list(token=args.token,id=args.id)
		data=json.loads(r.content)
		print json.dumps(data,sort_keys=True,indent=4,separators=(',',':'))

	def download_image(args):
                if args.url:
                        c=Client(args.url)
                else:
                         c=Client(PSAR_URL)
		c.get_image_file(path=args.path,psa_id=args.id,token=args.token)
        def upload_image(args):
                if args.url:
                        c=Client(args.url)
                else:
                         c=Client(PSAR_URL)
		c.put_image_file(psa_id=args.id,path=args.path,disk_format=args.disk_format,container_format=args.container_format,token=args.token)
        def delete_image(args):
                if args.url:
                        c=Client(args.url)
                else:
                         c=Client(PSAR_URL)
		c.delete_image(psa_id=args.id,token=args.token)    
	def download_manifest(args):
                if args.url:
                        c=Client(args.url)
                else:
                         c=Client(PSAR_URL)
		r=c.get_manifest(psa_id=args.id,token=args.token)
		with open(args.path,'w') as f:
			f.write(r.content)
	def upload_manifest(args):
                if args.url:
                        c=Client(args.url)
                else:
                         c=Client(PSAR_URL)
		c.put_manifest_file(psa_id=str(args.id),path=args.path,token=args.token)
	def delete_manifest(args):
                if args.url:
                        c=Client(args.url)
                else:
                         c=Client(PSAR_URL)
		c.delete_manifest_file(psa_id=args.id,token=args.token)
	def download_plugin(args):
                if args.url:
                        c=Client(args.url)
                else:
                         c=Client(PSAR_URL)
        	c.get_plugin_file(path=args.path,psa_id=args.id,token=args.token)

	def upload_plugin(args):
                if args.url:
                        c=Client(args.url)
                else:
                         c=Client(PSAR_URL)
        	c.put_plugin_file(psa_id=args.id,path=args.path,token=args.token)
	def delete_plugin(args):
                if args.url:
                        c=Client(args.url)
                else:
                         c=Client(PSAR_URL)
        	c.delete_plugin_file(psa_id=args.id,token=args.token)
	def create_psa(args):
                if args.url:
                        c=Client(args.url)
                else:
                         c=Client(PSAR_URL)
		r=c.create_psa()
		print r.text
	def delete_psa(args):
                if args.url:
                        c=Client(args.url)
                else:
                         c=Client(PSAR_URL)
		r=c.delete_psa(args.id)		
	
	#General
	parser=argparse.ArgumentParser(description="Command line client for the PSAR API")
	subparsers = parser.add_subparsers(help='groups')
	
	create_parser=subparsers.add_parser('create',help='Creates a new empty PSA')
	create_parser.add_argument('--url',action='store', help='URL of the PSAR')
	create_parser.add_argument('--token',action='store', help='Authentication token')

	create_parser.set_defaults(func=create_psa)
	
	delete_parser=subparsers.add_parser('delete',help='Deletes the PSA')
        delete_parser.add_argument('--url',action='store', help='URL of the PSAR')
        delete_parser.add_argument('id',action='store', help='ID of the PSA to delete')
	delete_parser.add_argument('--token',action='store', help='Authentication token')

	delete_parser.set_defaults(func=delete_psa)

	list_parser = subparsers.add_parser('list', help='List PSAs stored')
        list_parser.add_argument('--id', action='store', help='Returns only matching PSAs')
        list_parser.add_argument('--url',action='store', help='URL of the PSAR')
        list_parser.add_argument('--token',action='store', help='Authentication token')

        list_parser.set_defaults(func=list_psa)

	#Images
	image_parser=subparsers.add_parser('image',help='Interacts with the images')
	image_subparser=image_parser.add_subparsers(help='commands')
	
	#	Download
	download_image_parser=image_subparser.add_parser('download',help='Download an image')
	download_image_parser.add_argument('id', action='store', help='PSA to download')
	download_image_parser.add_argument('path', action='store', help='Path')
	download_image_parser.add_argument('--url',action='store', help='URL of the PSAR')
	download_image_parser.add_argument('--token',action='store', help='Authentication token')

	download_image_parser.set_defaults(func=download_image)
	
	
	#	Upload
	upload_image_parser=image_subparser.add_parser('upload', help='Upload an image')
	upload_image_parser.add_argument('id', action='store', help='PSA to upload')
	upload_image_parser.add_argument('path', action='store', help='Path')
	upload_image_parser.add_argument('--disk_format', required=True, choices=['qcow2', 'raw', 'vhd', 'vmdk', 'vdi', 'iso', 'aki','ari','ami'] , action='store', help='Disk format')
	upload_image_parser.add_argument('--container_format', required=True, choices=['bare', 'ovf', 'aki', 'ari', 'ami'], action='store', help='Container format')
	upload_image_parser.add_argument('--name', action='store', help='Name')
	upload_image_parser.add_argument('--status', action='store', help='status')
	upload_image_parser.add_argument('--manifest_id', action='store', help='Manifest ID')
	upload_image_parser.add_argument('--storage_id', action='store', help='Storage ID')
	upload_image_parser.add_argument('--plugin_id', action='store', help='Plugin ID')
	upload_image_parser.add_argument('--url',action='store', help='URL of the PSAR')
	upload_image_parser.add_argument('--token',action='store', help='Authentication token')


	upload_image_parser.set_defaults(func=upload_image)


	#	Delete
	delete_image_parser=image_subparser.add_parser('delete', help='Delete an image')
        delete_image_parser.add_argument('id', action='store', help='PSA to delete')
	delete_image_parser.add_argument('--url',action='store', help='URL of the PSAR')
	delete_image_parser.add_argument('--token',action='store', help='Authentication token')

	delete_image_parser.set_defaults(func=delete_image)


	#Manifest
	manifest_parser=subparsers.add_parser('manifest', help='Interacts with the manifests')
	manifest_subparser=manifest_parser.add_subparsers(help='commands')

        #       Download
        download_manifest_parser=manifest_subparser.add_parser('download',help='Download a manifest')
        download_manifest_parser.add_argument('id', action='store', help='ID of the PSA which manifest is to be downloaded')
        download_manifest_parser.add_argument('path', action='store', help='Path')
       	download_manifest_parser.add_argument('--url',action='store', help='URL of the PSAR')
	download_manifest_parser.add_argument('--token',action='store', help='Authentication token')

	download_manifest_parser.set_defaults(func=download_manifest)


        #       Upload
        upload_manifest_parser=manifest_subparser.add_parser('upload', help='Upload a manifest')
        upload_manifest_parser.add_argument('id', action='store', help='ID of the PSA which manifest is to be uploaded')
        upload_manifest_parser.add_argument('path', action='store', help='Path')
       	upload_manifest_parser.add_argument('--url',action='store', help='URL of the PSAR')
	upload_manifest_parser.add_argument('--token',action='store', help='Authentication token')

	upload_manifest_parser.set_defaults(func=upload_manifest)


        #       Delete
        delete_manifest_parser=manifest_subparser.add_parser('delete', help='Delete a manifest')
        delete_manifest_parser.add_argument('id', action='store', help='ID of the PSA which manifest is to be deleted')
       	delete_manifest_parser.add_argument('--url',action='store', help='URL of the PSAR')
	delete_manifest_parser.add_argument('--token',action='store', help='Authentication token')

	delete_manifest_parser.set_defaults(func=delete_manifest)
	
	
	#Plugins
        plugin_parser=subparsers.add_parser('plugin', help='Interacts with the plugins')
	plugin_subparser=plugin_parser.add_subparsers(help='commands')


        #       Download
        download_plugin_parser=plugin_subparser.add_parser('download',help='Download a plugin')
        download_plugin_parser.add_argument('id', action='store', help='PSA to download')
        download_plugin_parser.add_argument('path', action='store', help='Path')
       	download_plugin_parser.add_argument('--url',action='store', help='URL of the PSAR')
	download_plugin_parser.add_argument('--token',action='store', help='Authentication token')

	download_plugin_parser.set_defaults(func=download_plugin)


        #       Upload
        upload_plugin_parser=plugin_subparser.add_parser('upload', help='Upload a plugin')
        upload_plugin_parser.add_argument('id', action='store', help='PSA to upload')
        upload_plugin_parser.add_argument('path', action='store', help='Path')
        upload_plugin_parser.set_defaults(func=upload_plugin)
	upload_plugin_parser.add_argument('--url',action='store', help='URL of the PSAR')
	upload_plugin_parser.add_argument('--token',action='store', help='Authentication token')


        #       Delete
        delete_plugin_parser=plugin_subparser.add_parser('delete', help='Delete a plugin')
        delete_plugin_parser.add_argument('id', action='store', help='PSA to delete')
       	delete_plugin_parser.add_argument('--url',action='store', help='URL of the PSAR')
	delete_plugin_parser.add_argument('--token',action='store', help='Authentication token')

	delete_plugin_parser.set_defaults(func=delete_plugin)	

	

	args= parser.parse_args()
	args.func(args)
