def mean(a):
   return sum(a) / float(len(a))

# sample variance, not population variance
def variance(a):
   mu = mean(a)

   def differenceSquared(x):
      return float((x - mu)**2)

   return sum(map(differenceSquared, a)) / float(len(a) - 1)

# sample standard deviation, not population standard deviation
def standardDeviation(a):
   return variance(a)**0.5
