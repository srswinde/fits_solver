from imsolve import mont4k


m=mont4k('data/pointing0037.fits')
m.foobar = 'foobar'



print m
print m.solve_ext(1)
