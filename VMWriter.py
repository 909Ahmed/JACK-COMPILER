kind_to_segment = {'static': 'static',
                  'field': 'this',
                   'arg': 'argument',
                   'argument': 'argument',
                   'constant' : 'constant',
                   'local' : 'local',
                   'temp' : 'temp',
                   'that' : 'that',
                   'var': 'local',
                   'pointer': 'pointer'}

opr = {
	'+' : "add",
     '-' : "sub", 
  	'*':"call Math.multiply 2", 
     '/':"call Math.divide 2",
     '&':"and",
     '|':"or", 
	'<':"lt" ,
	'>':"gt" ,
	'=':"eq",
	'neg':"neg", 
	'not':"not" ,
}

class VMWriter:

	def __init__(self, ostream):
		self.ostream = ostream
		self.label_count = 0

	def write_ifgoto(self, label):
		self.ostream.write('if-goto ' + str(label) + '\n')

	def write_goto(self, label):
		self.ostream.write('goto ' + str(label)+"\n")

	def write_Label(self, label):
		self.ostream.write('label '+str(label)+'\n')

	def write_function(self, func, args):
		self.ostream.write('function ' + func + ' ' + str (args) + '\n')

	def write_return(self):
		self.ostream.write('return\n')

	def write_call(self, func_name, arg_count):
		self.ostream.write('call ' +  func_name + ' ' +str(arg_count) + '\n')

	def write_pop(self, type, counter):
		if (type == "field"):
			self.ostream.write("pop this " + str(counter) + '\n')
		else:
			self.ostream.write("pop " + type + ' ' + str(counter) + '\n')
            
	def write_push(self, type, counter, array=False):
		segment = kind_to_segment[type]
		if segment == 'this' and array:
			segment = 'that'
		self.ostream.write('push ' +  segment + ' ' +str(counter) + '\n')

	def writeArthimetcs(self, op):
		self.ostream.write(str(opr[op]) + '\n')
