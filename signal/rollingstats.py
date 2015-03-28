#!/usr/bin/python

class RunningSum(object):
	"""rs = RunningSum(); rs.add(3)
	
	This class supports fractions and interactions between fractions, integers, and floats."""
	def __init__ (self,num=0,denom=1):
		from types import FloatType
		if type(num)==FloatType:
			f = DecToFraction(num)
			self.numerator = f.numerator
			self.denominator = f.denominator
		else:
			self.numerator= num
			if denom > 0:
				self.denominator= denom
			else:
				self.numerator = -self.numerator
				self.denominator=-denom
		self._standardize()
		
	def _standardize(self):
		"""Fractions should have integer numerator and denominators, not decimals or floats"""
		ok = 0
		while not ok:
			try:
				if float(int(self.denominator))==float(self.denominator):
					ok = 1
				else:
					self.denominator *= 10
					self.numerator *= 10
			except:
				ok = 1
				self.numerator = int(self.numerator)
				self.denominator = int(self.denominator)
				
	def _fractionize(self,fract2):
		"Create a fraction representation of whatever we've been given"
		from types import IntType,FloatType
		if type(fract2)==IntType: 
			fract2 = RunningSum(fract2*self.denominator,self.denominator)
		elif type(fract2)==FloatType: 
			fract2 = RunningSum(fract2)
		#elif fract2.__class__.__name__ == "RunningSum":
		elif isinstance(fract2,RunningSum):
			fract2 = fract2
		else:
			raise FractionError, "Can't turn object into a fraction"
		return fract2
			
	def __repr__(self):
		if self.denominator == 1:
			return "%s" % (self.numerator,)
		elif self.numerator == 0:
			return "0"
		else:
			return "%s/%s" %(self.numerator,self.denominator)
		
	def toString(self):
		return self.__repr__()

	def toDecimal(self):
		"""f.toDecimal() 
		
		Returns a float value representation of the fraction f.
		"""
		return float(self.numerator)/self.denominator

	def mixedNumber(self):
		"""f.mixedNumer()
		
		Returns a string representation of the fraction.
		If the numerator is 0, mixedNumber returns '0'
		If the fraction represents an integer (eg. 4/2), mixedNumber() returns the
			integer as a string
		If the numerator is negative, the negative sign will be placed in front of
			the whole number
		If the whole number is 0 (eg. 2/3 as 0 2/3), mixedNumber returns a string
			without a whole number.
		"""
		if self.numerator < 0:
			neg = 1
			self.numerator = -self.numerator
		else: neg = 0
		whln = self.numerator/self.denominator # whole number
		
		newn = self.numerator - whln*self.denominator
		if neg: # Put things back where they belong
			whln = -whln
			self.numerator = -self.numerator 
		if whln: 
			if newn:
				return str(whln)+" "+RunningSum(newn,self.denominator).toString()
			else:
				return str(whln)
		else:
			return RunningSum(newn,self.denominator).toString()
			
	def recip(self):
		"""f.recip()
		
		Returns the reciprocal of the fraction.
		"""
		return RunningSum(self.denominator,self.numerator)
		
	def reduce(self):
		"""f.reduce() 
		
		Reduces f to it's simplest form. After calling reduce() the fraction's 
		numerator and denominator will not have a common divisor.
		"""
		divisor= gcd(self.numerator,self.denominator)
		if divisor > 1:
			if self.numerator < 0:
				neg =1
				self.numerator = -self.numerator
			else: neg = 0
			self.numerator = self.numerator/divisor
			if neg: self.numerator = -self.numerator
			self.denominator= self.denominator/divisor

	def __add__(self,fract2):
		fract2 = self._fractionize(fract2)
		sum = RunningSum()
		sum.numerator = (self.numerator*fract2.denominator)+(fract2.numerator*self.denominator)
		sum.denominator = (self.denominator*fract2.denominator)
		if sum.numerator > 0:
			sum.reduce()
		else:
			sum.numerator = -1*sum.numerator
			sum.reduce()
			sum.numerator = -1*sum.numerator
		return sum

	def __sub__(self,fract2):
		fract2 = self._fractionize(fract2)
		negative= RunningSum(-1*fract2.numerator,fract2.denominator)
		return self + negative

	def __mul__(self,fract2):
		fract2 = self._fractionize(fract2)
		product = RunningSum()
		product.numerator = self.numerator*fract2.numerator
		product.denominator = self.denominator*fract2.denominator
		if product.denominator < 0:
			product.denominator = -1*product.denominator
			product.reduce()
			product.numerator = -1*product.numerator
		elif product.numerator < 0:
			product.numerator = -1*product.numerator
			product.reduce()
			product.numerator = -1*product.numerator
		else:
			product.reduce()
		return product

	def __div__(self,fract2):
		fract2 = self._fractionize(fract2)
		return self * fract2.recip()

	def __iadd__(self,fract2):
		fract2 = self._fractionize(fract2)
		return self + fract2

	def __isub__(self,fract2):
		fract2 = self._fractionize(fract2)
		return self - fract2

	def __imul__(self,fract2):
		fract2 = self._fractionize(fract2)
		return self * fract2

	def __idiv__(self,fract2):
		fract2 = self._fractionize(fract2)
		return self / fract2

	def __radd__(self,fract2):
		fract2 = self._fractionize(fract2)
		return self + fract2

	def __rsub__(self,fract2):
		fract2 = self._fractionize(fract2)
		return fract2 - self

	def __rmul__(self,fract2):
		fract2 = self._fractionize(fract2)
		return self * fract2

	def __rdiv__(self,fract2):
		fract2 = self._fractionize(fract2)
		return fract2 / self
		
	def __eq__(self,fract2):
		fract2 = self._fractionize(fract2)
		return (self.numerator*fract2.denominator)==(self.denominator*fract2.numerator)
	
	def __cmp__(self,fract2):
		fract2 = self._fractionize(fract2)
		return cmp((self.numerator*fract2.denominator),(self.denominator*fract2.numerator))

	def __neg__(self):
		t= RunningSum(self.numerator*-1,self.denominator)
		t.reduce()
		return t
		
	def __float__(self):
		return self.toDecimal()
	
	def __int__(self):
		if self.numerator < 0:
			res = -(-self.numerator/self.denominator)
		else:
			res = self.numerator/self.denominator
		return res
		
	def tuple(self):
		"""f.tuple() 
		
		Returns the numerator and denominator of the fraction as a tuple.
		"""
		return (self.numerator,self.denominator)
		
	def __pow__(self,p):
		if p < 0:
			return RunningSum(pow(self.denominator,-p),pow(self.numerator,-p))
		else:
			return RunningSum(pow(self.numerator,p),pow(self.denominator,p))
	
	def mixedTuple(self):
		"""f.mixedTuple()
		
		Returns the results of f.mixedNumber() as a tuple of three integers.
		"""
		if self.numerator < 0:
			neg = 1
			self.numerator = -self.numerator
		else: neg = 0
		whln = self.numerator/self.denominator # whole number
		
		newn = self.numerator - whln*self.denominator
		if neg: # Put things back where they belong
			whln = -whln
			self.numerator = -self.numerator
		return (whln,newn,self.denominator)
	

class SimplisticRunningSum(object):
    
    def __init__(self):
        self.count = 0
        self.sum = 0

    def _add(self, other):
        self.count += 1
        self.sum += other
        return self.sum

    def __radd__(self, other):
        return self._add(other)

    def __add__(self, other):
        return self._add(other)
 
if __name__=="__main__":
    rs = RunningSum()
    for i in range(5):
        rs += i + 0.0
        print rs, type(rs)