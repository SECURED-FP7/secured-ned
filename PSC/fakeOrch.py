import falcon
import json
# from getGraph import getGraph
# from createPSA import createPSA
# from getConf import getConf

class getGraph():

	def on_get(self, req, rep):
		fp = open("./orch/profileType_ex2.json", "r")
		read = fp.read()
		print read
		rep.body = json.dumps(read, 'utf-8')
                rep.status = falcon.HTTP_200


class createPSA():
        
        def on_get(self, req, rep):
            pass 

	def on_put(self, req, rep):
		print json.load(req.stream)
                rep.status = falcon.HTTP_200


class getConf():

	def on_get(self, req, rep):
		fp = open("./orch/psaConf_ex.json", "r")
		read = fp.read()
		print read
		rep.body = json.dumps(read, 'utf-8')
		rep.status = falcon.HTTP_400

g = getGraph()
p = createPSA()
c = getConf()

app = falcon.API()
app.add_route('/getGraph', g)
app.add_route('/createPSA', p)
app.add_route('/getConf', c)
