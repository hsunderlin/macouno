'''
UTILITIES

For use in combination with the snet_core
'''
import mathutils, bpy, math
from time import time
from copy import copy
from macouno.snet_core import *

	

# Make coordinates for every point in the volume (not needed if you use GetLocation
def SNet_MakeCoords(len, res):

	coords = []
	
	# Make a coordinate for every point in the volume
	x = y = z = 0
	for i in range(len):
		
		# Should not be a vector yet... we'll do that when retrieving
		coords.append((x, y, z))

		# Go up a level if you move beyond the x or y resolution
		x += 1
		if x == res[0]:
			x = 0
			y += 1
		if y == res[1]:
			y = 0
			z += 1

	return coords
	
	
	
def SNet_GetLocation(position, gridRes):

	res = gridRes
	
	xRes = res[1]

	# The total nr of positions per layer
	layer = res[0] * xRes
	
	# The relative position on the final z layer
	xyRes = position % layer
	
	# The z position
	z = (position - xyRes) / layer
	
	x = xyRes % xRes
	
	y = (xyRes - x) / xRes
	
	return mathutils.Vector((x,y,z))
	
	
	
# Check to see if n is on the border of 
def SNet_IsGridEnd(n, gridX, gridY, gridLevel, gridLen, gridRes):

	# At the bottom level
	if n < gridLevel * 2:
		return True
		
	# At the top level
	elif n >= (gridLen - (gridLevel*2)):
		return True
		
	# Find the position at this level
	lvlPos = (n % gridLevel)
	
	# Now find the position in the gridX
	xPos = lvlPos % gridY
	
	if xPos <= 1 or xPos >= (gridX-2):
		return True
	
	# Clean way to find the y position
	# First discard the x location
	lvlPos -= xPos
	
	# Now divide by the y length
	yPos = lvlPos / gridY
	
	if yPos <= 1 or yPos >= (gridY-2):
		return True

	return False
	
	
	
	
# Limit a value to a global max and minimum
def SNet_LimitValue(n, limitMax, limitMin):
	if n > limitMax:
		return limitMax
	elif n < limitMin:
		return limitMin
	return n
	
	
	
# Make a sphere in the middle of the grid
def SNet_MakeBall(stateList, targetList, gridX, gridY, gridZ, gridLevel, gridLen, limitMax, limitMin, gridRes, coords, useCoords):

	# Let's make a ball within a certain distance from the middle
	middle = mathutils.Vector(((gridX-1)*0.5,(gridY-1)*0.5,(gridZ-1)*0.5))
	'''
	# Option to put an empty at the middle
	bpy.ops.object.empty_add(type='PLAIN_AXES', radius=10.0, view_align=False, location=middle)
	ob = bpy.context.active_object
	ob.name = 'True'
	ob.show_name = False
	'''
	
	for i in range(gridLen):
	
		if not SNet_IsGridEnd(i, gridX, gridY, gridLevel, gridLen, gridRes):
	
			distV = middle - SNet_GetCoord(i, gridRes, useCoords, coords)
			dist = distV.length
			
			val = round((dist -3.0), 2)
			
			if dist < 1.0:
				val = -1.0
				# SET A STATE!
				print("STARTING POINT",i)
				stateList[i] = 0
			
			targetList[i] = SNet_LimitValue(val, limitMax, limitMin)
				
		# Extra bit that adds empties ont he outer edges
		elif False:
			bpy.ops.object.empty_add(type='PLAIN_AXES', radius=0.01, view_align=False, location=SNet_GetCoord(i, gridRes, useCoords, coords))
			ob = bpy.context.active_object
			ob.name = 'True'
			ob.show_name = False
			
	return targetList, stateList
	
	

# Grow a stick like shape from the middle out
def SNet_MakeStick(stateList, targetList, gridX, gridY, gridZ, gridLevel):

	# Let's make a ball within a certain distance from the middle
	middle = mathutils.Vector((gridX*0.5, gridY*0.5, gridZ*0.5))
	
	m = SNet_GetGridMiddle(gridX, gridY, gridZ, gridLevel)
	stateList[m] = 0
	targetList[m] = -1
	
	near = []
	near = SNet_GetGridX(m, near, 10, gridX)
	
	for n in near:
		targetList[n] = -1
		
	return targetList


	
# Get the midpoint of the grid
def SNet_GetGridMiddle(gridX, gridY, gridZ, gridLevel):

	xLoc = round(gridX*0.5)
	yLoc = math.floor(gridY*0.5)
	zLoc = math.floor(gridZ*0.5)
	
	zDist = gridLevel * zLoc
	yDist = gridX * yLoc
	
	return xLoc + zDist + yDist



# Get the coord for this point
def SNet_GetCoord(n, gridRes, useCoords, coords):

	if useCoords:
		return mathutils.Vector(coords[n])
	
	return SNet_GetLocation(n, gridRes)



# Get the next and previous items on one axis
def SNet_GetGridX(n, near, steps, gridX):

	if steps < 0:
		for i in range(-(steps)):
			s = i+1
			ns = n-s
			# Haal de volgende op als deze niet aan het begin zit
			if ns > 1 and (ns % gridX) > 1:
				near.append(ns)
			else:
				return near
				
	else:
		
		for i in range(steps):
			ns = (n+1)+i
			# Get the next point if we're not at the end
			if ns % gridX:
				near.append(ns)
			else:
				return near

	return near



# Find the points on the next level
def SNet_GetGridY(n, near, steps, gridX, gridLevel):

	if steps < 0:
	
		for i in range(-(steps)):
			s = (i+1) * gridX
			ns = n - s
			# We want to know the placing on the current level!
			thisLvl = ns % gridLevel
			if thisLvl >= gridX:
				near.append(ns)
			else:
				return near
				
	else:
	
		for i in range(steps):
			s = (i+1) * gridX
			ns = n + s
			thisLvl = ns % gridLevel
			if thisLvl < (gridLevel - gridX):
				near.append(ns)
			else:
				return near
		
	return near



def SNet_GetGridZ(n, near, steps, gridLevel, gridCnt):

	if steps < 0:
	
		for i in range(-(steps)):
			s = (i+1) * gridLevel
			ns = n - s
			thisLvl = math.floor(ns / gridLevel)
			if thisLvl > 1.0:
				near.append(ns)
			else:
				return near
				
	else:
	
		for i in range(steps):
			s = (i+1) * gridLevel
			ns = n + s
			thisLvl = math.floor(ns / gridLevel)
			if thisLvl < (gridCnt):
				near.append(ns)
			else:
				return near

	return near



# Get all adjacent points
def SNet_GetGridNear(i, steps, gridX, gridLevel, gridCnt, stateList):
	
	near = []

	# Get the next items on this level
	near = SNet_GetGridX(i, near, -steps, gridX)
	if 1000 in near: print('Found at X 1')
	near = SNet_GetGridX(i, near, steps, gridX)
	if 1000 in near: print('Found at X 2')
	near = SNet_GetGridY(i, near, -steps, gridX, gridLevel)
	if 1000 in near: print('Found at Y 1')
	near = SNet_GetGridY(i, near, steps, gridX, gridLevel)
	if 1000 in near: print('Found at Y 2')
	near = SNet_GetGridZ(i, near, -steps, gridLevel, gridCnt)
	if 1000 in near: print('Found at Z 1')
	near = SNet_GetGridZ(i, near, steps, gridLevel, gridCnt)
	if 1000 in near: print('Found at Z 2')
	
	return near

	


# Find out how much time elapsed since the last iteration
# So this iteration is a percentage of the total (being 100%)
# This is the percentage to add to the state!
def SNet_TimeFactor(animate, lastMod, growTime):
	
	if animate == 'ANI':
		
		fps = bpy.context.scene.render.fps
		
		# Let's make it 24fps for now
		totalTime = growTime * fps
		
		factor = 100.0 / totalTime
		
		return factor
	
	else:
		now = time()
		
		elapsed = now - lastMod
		
		if elapsed <= 0.0:
			return 0.0
		
		factor = growTime / elapsed
		
		# Factor as a float
		factor = 1.0 / factor
		
		# But what we want is in percentages
		factor *= 100.0

	return factor
	
	
	

# Finish growing (really for after animation)
def SNet_FinishShape(shapeObject, animate):

	if animate == 'ANI':
		
		ob = shapeObject
		
		scn = bpy.context.scene
		
		scn.frame_current = ob['SNet_frameCurrent']
		scn.frame_start = ob['SNet_frameStart']
		scn.frame_end = ob['SNet_frameEnd']




def SNet_GrowStep(ob):	

	timeFactor = SNet_TimeFactor(ob['SNet_animate'], ob['SNet_lastMod'], ob['SNet_growTime'])
	
	ob['SNet_lastMod'] = time()
	
	# Retrieve the variables we need
	animate = ob['SNet_animate']
	currentList = ob['SNet_currentList']
	targetList = ob['SNet_targetList']
	stateList = ob['SNet_stateList']
	gridX = ob['SNet_gridX']
	gridY = ob['SNet_gridY']
	gridLevel = ob['SNet_gridLevel']
	gridLen = ob['SNet_gridLen']
	gridRes = ob['SNet_gridRes']
	gridCnt = ob['SNet_gridCnt']
	centerObject = ob['SNet_centerObject']
	
	# Stop growing if nothing can be found!
	growing = False
	

	if animate == 'NON':

		SNet_ApplyShape(ob, gridRes, targetList, centerObject)
		currentList = [t for t in targetList]
		stateList = array('f', minus_of(gridLen))

		
	else:
	
		for i, target in enumerate(targetList):
		
			oldState = stateList[i]
			
			# If this location is growing... we know what to do!
			if oldState >= 0:

			
				newState = oldState + timeFactor
				
				# Keep growing!
				growing = True
				
				newState = oldState + timeFactor
				
				# Start my neighbours
				if oldState < 50 and newState >= 50:
					
					near = SNet_GetGridNear(i, 1, gridX, gridLevel, gridCnt, stateList)
					
					for n in near:
					
						if stateList[n] < 0:
							if targetList[n] != currentList[n]:
								stateList[n] = 0
				
				# If we haven't reached the end of the growth cycle...
				if newState < 100:
						

					dif = targetList[i] - currentList[i]
					
					dif /= (100 - oldState)
					
					dif *= timeFactor
				
					currentList[i] += dif
	
					stateList[i] = newState
					
				# If the state has reached its maximum we are done growing
				else:
					
					currentList[i] = targetList[i]

					stateList[i] = -1.0

		
		if growing:
			SNet_ApplyShape(ob, gridRes, currentList, centerObject)
	
	ob['SNet_growing'] = growing
	ob['SNet_currentList'] = currentList
	ob['SNet_stateList'] = stateList
	
	if animate == 'ANI':
		scn = bpy.context.scene
		scn.frame_start = scn.frame_end = scn.frame_current
		bpy.ops.render.render(animation=True)
		scn.frame_current += 1
	
	if not growing:
		SNet_FinishShape(ob, animate)
	
	



def SNet_ApplyShape(shapeObject, gridRes, currentList, centerObject):

	mesher = SurfaceNetMesher()

	# Create the meshed volume
	meshed_volume = mesher.mesh_volume(*Volume(dimms = gridRes, data = currentList))
	#meshed_volume = mesher.mesh_volume(*dot)
	
	# Apply the volume data to the mesh
	shapeObject.data = mesh_from_data(shapeObject.data, *meshed_volume)
	
	if centerObject:
	
		min = [False, False, False]
		max = [False, False, False]

		for v in shapeObject.data.vertices:
		
			for i in range(3):
				co = v.co[i]
				if min[i] is False or co < min[i]:
					min[i] = co			
				if max[i] is False or co > max[i]:
					max[i] = co		
				
	max = mathutils.Vector(max)
	min = -mathutils.Vector(min)
	mid = max + min
	mid *= 0.5
	
	off = min
	off[0] -= mid[0]
	off[1] -= mid[1]
	
	#off = mathutils.Vector((-min[0]-((max[0] - min[0])*0.5),-(max[1] - min[1])*0.5)+min[1],	-min[2])
				
	# For now just set the object location because it's faster (apply location after we finish the object)
	shapeObject.location = off
	return
	
	
	#time.sleep(0.01)
	#bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=2)
	#scene_update.go()