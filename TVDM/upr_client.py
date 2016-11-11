from requests import get, put, post, delete
import json
class UPRClient:
        '''
        Client library for accessing the User Profile Repository (UPR) over HTTP REST
        '''

	def __init__(self,base_URL):
		self.base_URL=base_URL+'/v1/upr/'
		self.headers={"Accept":'application/json','Content-type':'application/json'}		

	def create_user(self, user_id, password, integrityLevel, type, 
			is_cooperative, is_infrastructure, is_admin, creator=None,
			optimization_profile=None):
                """
                Create a new user in the UPR. If the user is a NED itself (to enforce 
                NED-specific policies) then is_infrastructure should be set to True.
                """
		url=self.base_URL+'users/'
		data={}
		data['user_id']=user_id
		data['password']=password
		data['integrityLevel']=integrityLevel
		data['is_cooperative']=is_cooperative
		data['is_infrastructure']=is_infrastructure
		data['is_admin']=is_admin
		if creator:
			data['creator']=creator
		data['type']=type
		if optimization_profile:
			data['optimization_profile']=optimization_profile
		r=post(url,data=json.dumps(data),headers=self.headers)
		return r

	def get_user_list(self,user_id=None):
                """
                Retrieve user information for all users or a specific user
                """
		url=self.base_URL+'users/'
		params={}
		if user_id is not None:
			params['user_id']=user_id

		r=get(url, params=params)
		return r

	def get_user_type(self, user_id):
                """
                Retrieve the type of user: normal or expert
                """
		url=self.base_URL+'users/'+user_id+'/UserType/'
		r=get(url)
		return r	
	def get_user_creator(self, user_id):
                """
                Get the username of an admin who created a specific user
                """
		url=self.base_URL+'users/'+user_id+'/Creator/'
		r=get(url)
		return r	
	def get_user_opt_profile(self, user_id):
                """
                Retrieve the user's specific optimisation preferences
                """
		url=self.base_URL+'users/'+user_id+'/OptProfile/'
		r=get(url)
		return r	
	def get_user_groups(self, user_id):
                """
                Get groups associated to a given user
                """
		url=self.base_URL+'users/'+user_id+'/Groups/'
		return get(url)
	def get_created_users(self,user_id):		
                """
                Get a list of users created by a given admin
                """
		url=self.base_URL+'users/'+user_id+'/CreatedUsers/'
		return get(url)
	
	def auth_user(self, user , password):
                """
                Contact authorisation service (OpenStack Keystone)
                """
		url=self.base_URL+'users/auth/'
		data={}
		data['username']=user
		data['password']=password

		r=post(url,data=json.dumps(data),headers=self.headers)
		return r
	def update_user(self, user_id,  name=None, password=None, integrityLevel=None, type=None, 
                        is_cooperative=None, is_infrastructure=None, is_admin=None, creator=None):
                """
                Update information for a specific user
                """
		url=self.base_URL+'users/'+str(user_id)+'/'
		
		data={}
		if name is not None:
			data['name']=name
		if password is not None:
			data['password']=password
		if integrityLevel is not None:
			data['integrityLevel']=integrityLevel
		if is_cooperative is not None:
			data['is_cooperative']=is_cooperative
		if is_infrastructure is not None:
			data['is_infrastructure']=is_infrastructure
		if is_admin is not None:
			data['is_admin']=is_admin
		if creator is not None:
			data['creator']=creator
		
		r=put(url, data=json.dumps(data),headers=self.headers)
		return r

	def delete_user(self,user_id):
                """
                Delete a specific user
                """
		url=self.base_URL+'users/'+str(user_id)+'/'
		r=delete(url)
		return r

	def get_user_psa(self,user_id,is_active=None):
                """
                Retrieve the list of PSAs for a particular user.
                Set is_active to True to get a list of enabled PSAs.
                """
		url=self.base_URL+'users/'+str(user_id)+'/PSA/'
		params={}
		if is_active is not None:
			params['is_active']=is_active
		return get(url,params=params)
	def put_user_psa(self,user_id,data=None,psa_id=None,active=None,running_order=None):
		"""
		Data must be in the form accepted by the UPR
		{'PSAList':[
                                {
                                        'psa_id':'12345',
                                        'active':true,
                                        'running_order':2
                                },
                                {
                                        'psa_id':'54321',
                                        'active':false,
                                        'running_order':1
                                }
                           ]
                        }
		"""
		url=self.base_URL+'users/'+str(user_id)+'/PSA/'
		if data:
			return put(url,data=data)
		else:
			psa_list={}
			psas=[]
			psa={}
			psa['psa_id']=psa_id
			psa['active']=active
			psa['running_order']=running_order
			psas=psas+[psa]
			psa_list['PSAList']=json.dumps(psas)
			return put(url,data=json.dumps(psa_list),headers=self.headers)
		
	def delete_user_psa(self,user_id,psa_id):
                """
                Delete a PSA from a user's profile
                """
		url=self.base_URL+'users/'+str(user_id)+'/PSA/'
		params={}
		params['psa_id']=str(psa_id)
		return delete(url,params=params)
	
	def get_hspl(self,target=None,editor=None):
                """
                Retrieve HSPL for a given user.
                Optionally specify additional constraints about who is the editor 
                and who is the target.
                """
		url=self.base_URL+'HSPL/'
		params={}
		if target is not None:
			params['target']=target
		if editor is not None:
			params['editor']=editor

		return get(url,params=params)
	def delete_hspl(self,user_id,hspl_id):
                """
                Delete a HSPL for a given user
                """
		url=self.base_URL+'HSPL/'
		params={}
		params['hspl_id']=hspl_id
		return delete(url,params=params)		

	def put_user_hspl(self, user_id, hspl, target):
                """
                Upload a HSPL for a given user
                """
		url=self.base_URL+'users/'+user_id+'/HSPL/'		
		data={}
		data['hspl']=hspl
		data['target']=target
		return put(url,data=json.dumps(data),headers=self.headers)

	def create_group(self, name, description):
                """
                Create a new group for users
                """
		url=self.base_URL+'groups/'
		data={}
		data['name']=name
		data['description']=description
		return post(url,data=json.dumps(data),headers=self.headers)
	
	def list_group(self):
                """
                List all groups
                """
		url=self.base_URL+'groups/'
		return get(url)
		
	def delete_group(self, group_id):
                """
                Delete a specific group
                """
		url=self.base_URL+'groups/'+group_id+'/'
		return delete(url)

	def update_group(self, group, description=None):
                """
                Update group information
                """
		url=self.base_URL+'groups/'+group+'/'
		data={}
		if description:
			data['description']=description
		return put(url,data=json.dumps(data),headers=self.headers)

	def list_user_group(self,group):
                """
                List all users in a group
                """
		url=self.base_URL+'groups/'+group+'/users/'
		return get(url)

	def associate_user_group(self, group, user_id):
                """
                Add a user to a group
                """
		url=self.base_URL+'groups/'+group+'/users/'
		data={}
		data['user_id']=user_id
		return put(url,data=json.dumps(data),headers=self.headers)

	def delete_user_group(self, user, group):
                """
                Delete a user group
                """
		url=self.base_URL+'groups/'+group+'/users/'
		params={}
		params['user_id']=user
		return delete(url,params=params)
	
	def get_group_psa(self, group):
                """
                Get list of PSAs associated with a group
                """
		url=self.base_URL+'groups/'+group+'/PSA/'
		return get(url)

	def put_group_psa(self, group, psa_id):
                """
                Add PSAs to a group
                """
		url=self.base_URL+'groups/'+group+'/PSA/'
		data={}
		data['psa_id']=psa_id
		return put(url,data=json.dumps(data),headers=self.headers)

	def delete_group_psa(self,group,psa_id):
                """
                Delete PSAs from a group
                """
		url=self.base_URL+'groups/'+group+'/PSA/'
		params={}
		params['psa_id']=psa_id
		return delete(url,params=params)

	#MSPL

	def get_mspl(self,internalID=None,target=None,editor=None,is_reconciled=False):
                """
                Retrieve MSPLs for a given user or editor. Set is_reconciled to True
                to only fetch reconciled policies.
                """
		url=self.base_URL+'MSPL/'
		params={}
		if internalID:
			params['internalID']=internalID
		if target:
			params['target']=target
		if editor:
			params['editor']=editor
		if is_reconciled:
			params['is_reconciled']=is_reconciled
		return get(url,params=params)
	
	def create_mspl(self,target,editor,capability,is_reconciled,mspl,internalID=None):
                """
                Upload an MSPL, specifying capability and if reconciled
                """
		url=self.base_URL+'MSPL/'
		data={}
		data['target']=target
		data['editor']=editor
		data['capability']=capability
		data['is_reconciled']=is_reconciled
		data['mspl']=mspl
		if internalID:
			data['internalID']=internalID
		return post(url,data=json.dumps(data),headers=self.headers)

	def delete_mspl(self,mspl_id=None,target=None,editor=None,capability=None,is_reconciled=None):
                """
                Delete a particular MSPL
                """
		url=self.base_URL+'MSPL/'
		params={}
		if mspl_id:
			params['mspl_id']=mspl_id
			return delete(url,params=params)
		if target:
			params['target']=target
		if editor:
			params['editor']=editor
		if capability:
			params['capability']=capability
		if is_reconciled is not None:
			params['is_reconciled']=is_reconciled
		return delete(url,params=params)

	def put_user_mspl_psa(self,user_id,psa_id,mspl_id):
                """
                Create association between a particular MSPL and a particular PSA
                """
		url=self.base_URL+'users/'+user_id+'/MSPL/'
		
		#json_data=json.loads('{"MSPL":[{"psa_id":'+str(psa_id)+',"mspl_id":'+str(mspl_id)+'}]}')
		
		data={}
		mspls=[]
		mspl={}
		mspl["psa_id"]=str(psa_id)
		mspl["mspl_id"]=mspl_id
		mspls=mspls+[mspl]
		data["MSPL"]=json.dumps(mspls)
		print data
		#headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
		return put(url,data=json.dumps(data),headers=self.headers)


	def get_user_mspl_psa(self,user_id):
                """
                Get MSPL-PSA association
                """
		url=self.base_URL+'users/'+user_id+'/MSPL/'
		return get(url)

	#AG
	def get_user_ag(self,target,editor=None):
                """
                Retrieve Application Graph for a particular user
                """
		url=self.base_URL+'users/'+target+'/AG'
		params={}
		if editor:
			params['editor']=editor
		return get(url,params=params)
	def delete_user_ag(self,target,editor):
                """
                Delete a user's application graph
                """
		url=self.base_URL+'users/'+target+'/AG'
		params={}
		params['editor']=editor
		return delete(url,params=params)
	def post_ag(self,target_id,editor_id,ag):
                """
                Upload application graph
                """
		url=self.base_URL+'users/AG/'
		data={}
		data['target_id']=target_id
		if editor_id is not None:
	                data['editor_id']=editor_id
		else:
			data['editor_id']=target_id
		data['application_graph']=ag
		return post(url,data=json.dumps(data),headers=self.headers)
	#RAG
	def get_user_rag(self,user_id):
                '''
                Retrieve stored reconciled application graph for a particular user
                '''
		url=self.base_URL+'users/'+user_id+'/RAG'
		return get(url)
	def delete_user_rag(self,user_id):
                '''
                Delete stored reconciled application graph for a particular user
                '''
		url=self.base_URL+'users/'+user_id+'/RAG'
		return delete(url)
	def post_rag(self,target_id,ned_info,rag):
                '''
                Store reconciled application graph in UPR
                '''
		url=self.base_URL+'users/RAG/'
		data={}
		data['target_id']=target_id
		data['ned_info']=ned_info
		data['reconcile_application_graph']=rag
		return post(url,data=json.dumps(data),headers=self.headers)

	#Low Level
	def get_user_psaconf(self,user_id,psa_id=None):
                '''
                Retrieve cached low level configurations
                '''
		url=self.base_URL+'users/'+user_id+'/PSAConf/'
		params={}
		if psa_id:
			params['psa_id']=psa_id
		return get(url,params=params)
	def post_psaconf(self,user_id,psa_id,configuration):
                '''
                Store low level configurations in UPR
                '''
		url=self.base_URL+'users/'+user_id+'/PSAConf/'
		data={}
		data['psa_id']=psa_id
		data['configuration']=configuration
		return post(url,data=json.dumps(data),headers=self.headers)
	def delete_user_psaconf(self,user_id,psa_id):
                '''
                Delete low level configurations
                '''
		url=self.base_URL+'users/'+user_id+'/PSAConf/'
		params={}
		params['psa_id']=psa_id
		return delete(url,params=params)		
	#Executed PSA
	def delete_executed_psa(self,user_id,psa_id):
		url=self.base_URL+'users/'+user_id+'/ExecutePSA/'
		params={}
		params['psa_id']=psa_id
		return delete(url,params=params)
		
	def get_executed_psa(self,user_id):
		url=self.base_URL+'users/'+user_id+'/ExecutePSA/'
		return get(url)
	def put_executed_psa(self,user_id,psa_id):
		url=self.base_URL+'users/'+user_id+'/ExecutePSA/'
		data={}
		data['psa_id']=psa_id
		print data
		return put(url,data=json.dumps(data),headers=self.headers)


	#Reconciliation Report

	def get_reconciliation_report(self,user_id,ned_info=None):
                '''
                Retrieves reconciliation report
                '''
		url=self.base_URL+'users/'+user_id+'/reconciliation_report/'
		params={}
		if ned_info:
			params['ned_info']=ned_info
		return get(url,params=params)

	def post_reconciliation_report(self,user_id,ned_info,reconciliation_report):
                '''
                Stores reconciliation report
                NED info is miscaleneous data about the NED which can be indexed with the report
                '''
		url=self.base_URL+'users/'+user_id+'/reconciliation_report/'
		data={}
		data['ned_info']=ned_info
		data['reconciliation_report']=reconciliation_report
		return post(url,data=data)
	
	def delete_reconciliation_report(self,user_id,ned_info=None):
                '''
                Delete stored reconciliation report
                '''
		url=self.base_URL+'users/'+user_id+'/reconciliation_report/'
		params={}
		if ned_info:
			params['ned_info']=ned_info

		return delete(url,params=params)
