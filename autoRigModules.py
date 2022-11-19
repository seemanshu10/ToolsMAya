import maya.cmds as cmds
import maya.mel as pm
import math as ma

def autoRigModules():
	
	# if working on rear leg 
	isRearLeg = 1
	
	# number of joints to be working on 
	limbJoints =4
	
	#check for selection is valid 	
	selection = cmds.ls(sl =1,type="joint") 
	
	if isRearLeg:
		limbType = "rear"
		print "working on rear leg"
		
	else:
		limbType = "front"
		print "working in the fron leg"
		
	
	#error check to make sure a joint is selected 
	if not selection:
		cmds.error ("Please select a valid joint")
	else:
		legJoint = cmds.ls(sl=1,type="joint")[0]
		#print legJoint
	#now we have a selected joint we can check for the prefix to see which side it is
	whichSide=legJoint[0:2]
	
	if not "l_" in whichSide:
		if not "r_" in whichSide:
			cmds.error("Please set a joint with a usable prefix of either l_ or r_")
			 
	
	limbName= whichSide+"leg_"+limbType
	
    #````````````````````````````````````````````````````````````````````````````````
	#find the children of the object 
	
	jointHierarchy =cmds.listRelatives(legJoint,ad =1 , type="joint")
	jointHierarchy.append(legJoint)
	jointHierarchy.reverse()
	#print jointHierarchy
	
	#build the list of hoints fk , ik , stretch chain joint 
	
	#duplicate the main joit chain and append the names 
	newJointList = ["_fk","_ik","_stretch"]
	
	#add an extra join chain driver for if rearleg is 1 
	if isRearLeg:
		newJointList.append("_driver")
	
	# build the joints
	for newJoint in newJointList:
		for i in range(limbJoints):
			newJointName = jointHierarchy[i]+newJoint
			
			#print newJointName
			
			cmds.joint(n=newJointName)
			cmds.matchTransform(newJointName,jointHierarchy[i])
			cmds.makeIdentity(newJointName,a=1, t=0,r=1,s=0)
			
		cmds.select(cl=1)
	
	#unparent the fk chain 
	parentjoint= cmds.select(jointHierarchy[0]+"_fk") 
	cmds.parent(w=1)
	
	#___________________________________________________________________________________
	#controls the main joint the ik and fk joints so we can blend between both ik and fk
	for i in range(limbJoints):
		cmds.parentConstraint((jointHierarchy[i]+"_fk"),(jointHierarchy[i]+"_ik"),jointHierarchy[i],w=1,mo=0)
	
	#___________________________________________________________________________________
	#setup Fk 
	
	#connect the fk controls to the new fk joint chains 
	for i in range(limbJoints):
		cmds.parentConstraint((jointHierarchy[i]+"_FK_Ctrl"),(jointHierarchy[i]+"_fk"),w=1,mo=1)
	
	#___________________________________________________________________________________			
	#setup Ik
	
	#if is the rear leg ,create the ik handle from the first to 3rf joints 
	if isRearLeg:
		 cmds.ikHandle(n=(limbName+"_driver_ikHandle"),sol="ikRPsolver",sj=(jointHierarchy[0]+"_driver"),ee=(jointHierarchy[3]+"_driver"))
	
	# create the main ik handle from femur to metacarpus 
	cmds.ikHandle(n=(limbName+"_knee_ikHandle"),sol="ikRPsolver",sj=(jointHierarchy[0]+"_ik"),ee=(jointHierarchy[2]+"_ik"))
	
	
	# create the hock ik handle ,from the metatarsus to the metacarpus
	cmds.ikHandle(n=(limbName+"_hock_ikHandle"),sol="ikSCsolver",sj=(jointHierarchy[2]+"_ik"),ee=(jointHierarchy[3]+"_ik"))
	
	#create the hock control offset group 
	cmds.group((limbName+"_knee_ikHandle"),n=(limbName+"_knee_control"))
	cmds.group((limbName+"_knee_control"),n=(limbName+"_knee_control_offset"))
	
	# find the ankle pivot 
	anklePivot = cmds.xform(jointHierarchy[3],q=1,ws=1,piv=1) 
	
	#set the pivot of offset groups to match the ankle pivot 
	cmds.xform(((limbName+"_knee_control"),(limbName+"_knee_control_offset")),ws=1,piv=(anklePivot[0],anklePivot[1],anklePivot[2]))
	
	pawCtr = (whichSide+limbType+"_paw_Ctrl")
	kneeCtr= (whichSide+limbType+"_knee_Ctrl")
	hockCtr= (whichSide+limbType+"_hock_Ctrl")
	rootCtr= (whichSide+limbType+"_hip_Ctrl")
	switchCtrl = (whichSide+limbType+"_Switch_Ctrl")
		
	#parent the ikHandle and the group to the paw ik control 
	cmds.parent((limbName+"_hock_ikHandle"),pawCtr)
	
	#if it is the rear leg ,adjust the hieraccy so the driver leg controls the ikHandles
	if isRearLeg:
		cmds.parent((limbName+"_knee_control_offset"),(jointHierarchy[2]+"_driver"))
		cmds.parent((limbName+"_hock_ikHandle"),(jointHierarchy[3]+"_driver"))
		
		cmds.parent((limbName+"_driver_ikHandle"),pawCtr)
	else:
		cmds.parent((limbName+"_knee_control_offset"),"root_Ctrl")
		cmds.pointConstraint(pawCtr,(limbName+"_knee_control_offset"),w=1,mo=1)	
	
	#make the paw ctrl drive the ankle joint to maintain orientation
	cmds.orientConstraint(pawCtr,(jointHierarchy[3]+"_ik"),w=1,mo=1)

	
	#add the pole vector to th ikHandle if its rear leg add in the diven ik handle , if its the front add it to the knee ikHandle 
	if isRearLeg:
		cmds.poleVectorConstraint(kneeCtr,(limbName+"_driver_ikHandle"),w=1)
	else:
		cmds.poleVectorConstraint(kneeCtr,(limbName+"_knee_ikHandle"),w=1) 
	
	#add hock control 
	
	cmds.shadingNode("multiplyDivide",au=1,n=(limbName+"_hock_multi")) 
	
	cmds.connectAttr((hockCtr+".translate"),(limbName+"_hock_multi.input1"),f=1)
	
	cmds.connectAttr((limbName+"_hock_multi.outputZ"),(limbName+"_knee_control.rotateX"),f=1)
	cmds.connectAttr((limbName+"_hock_multi.outputX"),(limbName+"_knee_control.rotateZ"),f=1)
	
	cmds.setAttr((limbName+"_hock_multi.input2X"),-2.5)
	cmds.setAttr((limbName+"_hock_multi.input2Z"),2.5)
	
	#---------------------------------------------------------------------------------------
	#add the ik fk blending 
	reverse=cmds.shadingNode("reverse",au=1,n=(limbName+"_Switch_Ctrl_reverse"))
	print (reverse)

	cmds.connectAttr((switchCtrl + ".ik_fk_Switch"), (reverse + ".input.inputX"), f=1)
	cmds.connectAttr((reverse + ".outputX"), (whichSide+limbType+ "_FK_Ctrl_GRP.visibility"), f=1)
	cmds.connectAttr((switchCtrl + ".ik_fk_Switch"),(whichSide+limbType+"_paw_Ctrl_GRP.visibility"), f=1)
	'''
	cmds.connectAttr((switchCtrl+".ik_fk_Switch"),(whichSide+limbType+"_FK_Ctrl_GRP.visibility"),f=1)
	cmds.connectAttr((switchCtrl+".ik_fk_Switch"),(reverse+".input.inputX"),f=1)
	'''
	for i in range(limbJoints):
		getContraint=cmds.listConnections(jointHierarchy[i],type="parentConstraint")[0]
		getWeights=cmds.parentConstraint(getContraint,q=1,wal=1)
		
		#adding the ik_fkSwitch
	
		cmds.connectAttr((switchCtrl+".ik_fk_Switch"),(getContraint+"."+getWeights[1]),f=1)
		cmds.connectAttr((limbName+"_Switch_Ctrl_reverse.outputX"),(getContraint+"."+getWeights[0]),f=1)
		
	#----------------------------------------------------------------------------------------------------
	#updated the hierarchy 
	
	#add a group for that limb
	cmds.group(em=1,n=(limbName+"_Grp"))
	cmds.matchTransform((limbName+"_Grp"),legJoint)
	cmds.makeIdentity((limbName+"_Grp"),a=1,t=1,r=1,s=0)
	
	#parent the joint chains to new group
	
	cmds.parent((legJoint+"_ik"),(legJoint+"_fk"),(legJoint+"_stretch"),(limbName+"_Grp"))
	
	if isRearLeg:
		cmds.parent((legJoint+"_driver"),(limbName+"_Grp"))
		  
	#make the new group follow the legRoot ctrl
	cmds.parentConstraint(rootCtr,(limbName+"_Grp"),w=1,mo=1)
	
	#-----------------------------------------------------------------------------------------------------
	#make stretchy 
	
	loc=cmds.spaceLocator(n=(limbName+"_stretchEndPos_Loc"))
	#move it to the ankle pos 
	cmds.matchTransform(loc,jointHierarchy[3])
	cmds.parent(loc,pawCtr)
	
	# start to build the distance nodes
	# first,we will need to to add all distances for joints 
	cmds.shadingNode("plusMinusAverage",au=1,n=(limbName+"_length"))
	
	#build the distance nodes for each section 
	for i in range(limbJoints):
		
		#ignore the last joint or it will try to use the toes 
		if i is not limbJoints -1:
			cmds.shadingNode("distanceBetween",au=1,n=(jointHierarchy[i]+"_distNode"))
			
			cmds.connectAttr((jointHierarchy[i]+"_stretch.worldMatrix"),(jointHierarchy[i]+"_distNode.inMatrix1"),f=1)
			cmds.connectAttr((jointHierarchy[i+1]+"_stretch.worldMatrix"),(jointHierarchy[i]+"_distNode.inMatrix2"),f=1)
			
			cmds.connectAttr((jointHierarchy[i]+"_stretch.rotatePivotTranslate"),(jointHierarchy[i]+"_distNode.point1"),f=1)
			cmds.connectAttr((jointHierarchy[i+1]+"_stretch.rotatePivotTranslate"),(jointHierarchy[i]+"_distNode.point2"),f=1)
			
			cmds.connectAttr((jointHierarchy[i]+"_distNode.distance"),(limbName+"_length.input1D["+str(i)+"]"),f=1)
			
	#now get the distance from the root to stretch end locator, check the leg is stretched or not 
	cmds.shadingNode("distanceBetween",au=1,n=(limbName+"_stretch_distNode"))
			
	cmds.connectAttr((jointHierarchy[0]+"_stretch.worldMatrix"),(limbName+"_stretch_distNode.inMatrix1"),f=1)
	cmds.connectAttr((limbName + "_stretchEndPos_Loc.worldMatrix"),(limbName+"_stretch_distNode.inMatrix2"),f=1)
			
	cmds.connectAttr((jointHierarchy[0]+"_stretch.rotatePivotTranslate"),(limbName+"_stretch_distNode.point1"),f=1)
	cmds.connectAttr((limbName+"_stretchEndPos_Loc.rotatePivotTranslate"),(limbName+"_stretch_distNode.point2"),f=1)
	
	#create nodes to check for stretching ,and to control how the stretch works 
	
	#scale factor compares the length og the leg with the stretch locator ,so we can see the leg is actually stretching 
	cmds.shadingNode("multiplyDivide",au=1,n=(limbName+"_scaleFactor"))
	
	#we use the condition node to pass this onto the joints, so the leg only stretches the way we want it to
	cmds.shadingNode("condition",au=1,n=(limbName+"_condition"))
	
	#adjust the node settings 
	cmds.setAttr((limbName+"_scaleFactor.operation"),2)
	
	cmds.setAttr((limbName+"_condition.operation"),2)
	cmds.setAttr((limbName+"_condition.secondTerm"),1)
	
	# connect the stretch distance to the scale factor with multiply divide node 
	cmds.connectAttr((limbName+"_stretch_distNode.distance"),(limbName+"_scaleFactor.input1X"),f=1)
	
	#connect the full leg distance to the scalefactor multiply divide node
	cmds.connectAttr((limbName+"_length.output1D"),(limbName+"_scaleFactor.input2X"),f=1)

	#next, connect the stretch factor node to the first term in the condition node 
	cmds.connectAttr((limbName+"_scaleFactor.outputX"),(limbName+"_condition.firstTerm"),f=1)
	
	#also connect it tot the color if true attribute,so we can use this as the stretch value
	cmds.connectAttr((limbName+"_scaleFactor.outputX"),(limbName+"_condition.colorIfTrueR"),f=1)
	
	for i in range(limbJoints):
		cmds.connectAttr((limbName+"_condition.outColorR"),(jointHierarchy[i]+"_ik.scaleX"),f=1)
		
		# also effect the driver skeelton , if this is the rear leg:
		if isRearLeg:
			cmds.connectAttr((jointHierarchy[i]+"_ik.scaleX"),(jointHierarchy[i]+"_driver.scaleX"),f=1)
			
	#add the ability to turn the stretchiness off 
	cmds.shadingNode("blendColors",au=1,n=(limbName+"_blendColors"))
	cmds.setAttr((limbName+"_blendColors.color2"),1,0,0,type = "double3")
	
	cmds.connectAttr((limbName+"_scaleFactor.outputX"),(limbName+"_blendColors.color1R"),f=1)
	cmds.connectAttr((limbName+"_blendColors.outputR"),(limbName+"_condition.colorIfTrueR"),f=1)
	
	#connect to the paw control attribute--
	cmds.select(pawCtr)
	cmds.addAttr(ln='Stretchiness',at ='double',min=0,max=1,dv=0,k=1)
	cmds.connectAttr((pawCtr+".Stretchiness"),(limbName+"_blendColors.blender"),f=1)
	
	#adding the stretchType attr to control 
	cmds.addAttr(ln='stretchType',at ='enum',k=1,en="Full:StretchOnly:SquashOnly:")
	
	#setting key driven for stretchType options 
	cmds.setAttr((pawCtr+".stretchType"),0)
	cmds.setAttr((limbName+"_condition.operation"),1) #not equal
	
	cmds.setDrivenKeyframe((limbName+"_condition.operation"),cd=(pawCtr+".stretchType"))
	
	cmds.setAttr((pawCtr+".stretchType"),1)
	cmds.setAttr((limbName+"_condition.operation"),3) #greater than 
	
	cmds.setDrivenKeyframe((limbName+"_condition.operation"),cd=(pawCtr+".stretchType"))
	
	cmds.setAttr((pawCtr+".stretchType"),2)
	cmds.setAttr((limbName+"_condition.operation"),5) #less or equal
	
	cmds.setDrivenKeyframe((limbName+"_condition.operation"),cd=(pawCtr+".stretchType"))
	
	cmds.setAttr((pawCtr+".stretchType"),1)
	
	cmds.select(cl=1)
	
	#-----------------------------------------------------------------------------------------------------
	#make volumeJoint
	#-----------------------------------------------------------------------------------------------------
	cmds.select(pawCtr)
	cmds.addAttr(ln='Volume_Offset',at ='double',min=-1,max=1,dv=-0.5,k=1)
	
	# first,we will need to to add all distances for joints 
	cmds.shadingNode("multiplyDivide",au=1,n=(limbName+"_volume"))
	
	cmds.setAttr((limbName+"_volume.operation"),3)
	
	#cooneect the main stretch value to the volume node
	cmds.connectAttr((limbName+"_blendColors.outputR"),(limbName+"_volume.input1X"),f=1)
	
	#cooneect the main stretch value to the volume node
	cmds.connectAttr((limbName+"_volume.outputX"),(limbName+"_condition.colorIfTrueG"),f=1)
	
	#connect to the fibula joint 
	cmds.connectAttr((limbName+"_condition.colorIfTrueG"),(jointHierarchy[1]+".scaleY"),f=1)
	cmds.connectAttr((limbName+"_condition.colorIfTrueG"),(jointHierarchy[1]+".scaleZ"),f=1)

	#connect to the metacarpus joint 
	cmds.connectAttr((limbName+"_condition.colorIfTrueG"),(jointHierarchy[2]+".scaleY"),f=1)
	cmds.connectAttr((limbName+"_condition.colorIfTrueG"),(jointHierarchy[2]+".scaleZ"),f=1)
	
	#connect to the main volume attributes 
	cmds.connectAttr((pawCtr+".Volume_Offset"),(limbName+"_volume.input2X"),f=1)
	
	#--------------------------------------------------------------------------------####
	####																			 ####
	#### 			Add roll joints 												 ####
	#--------------------------------------------------------------------------------####
	
	# check which side
	if whichSide =="l_":
		flipSide=1
	else:
		flipSide=-1
			
	#create the main roll and folllow joints 
	rollJointList = [jointHierarchy[0],jointHierarchy[3],jointHierarchy[0],jointHierarchy[0]]
	
	for i in range(len(rollJointList)):
		#Setup the joint names
		if i>2:
			rollJointName=rollJointList[i]+"_follow_tip"
		elif i>1:
			rollJointName=rollJointList[i]+"_follow"
		else:
			rollJointName=rollJointList[i]+"_roll"
			
		cmds.joint(n=rollJointName,rad=2)
		cmds.matchTransform(rollJointName,rollJointList[i])
		cmds.makeIdentity(rollJointName,a=1,t=1,r=1,s=0)
		
		if i<2:
			cmds.parent(rollJointName,rollJointList[i])
		elif i>2:
			cmds.parent(rollJointName,rollJointList[2]+"_follow")
			
		cmds.select( clear=True )
		
		#show the rotational axes to help us visualize the rotations
		#cmds.toggle(rollJointName,la=1)
		
	#lets work on the femur first and adjust the follow joints.
	cmds.pointConstraint(jointHierarchy[0],jointHierarchy[1],rollJointList[2]+"_follow_tip",w=1,mo=0,n="tempConstrain")
	cmds.delete("tempConstrain")		
		
	#now move them out
	cmds.move(0,0,-5*flipSide,(rollJointList[2]+"_follow"),r=1,os=1,wd=1)
	
	#create the aim locator whic hte femur roll joint will always follow 
	cmds.spaceLocator(n=(rollJointList[0]+"_roll_aim"))
	
	# move it to root joint and parent it to the follow joint so it moves with it 
	cmds.matchTransform((rollJointList[0]+"_roll_aim"),(rollJointList[2]+"_follow"))
	cmds.parent((rollJointList[0]+"_roll_aim"),(rollJointList[2]+"_follow"))
	
	#move the locator out too
	cmds.move(0,0,-5*flipSide,(rollJointList[0]+"_roll_aim"),r=1,os=1,wd=1)
	
	#make the root joint aim at the joint
	cmds.aimConstraint(jointHierarchy[1],(rollJointList[0]+"_roll"),w=1,aim=(1,0,0),u=(0,0,-1),wut="object",wuo=(rollJointList[0]+"_roll_aim"),mo=1)
	
	#add an ik handle so the follow joints,follow the leg 
	cmds.ikHandle(n=(limbName+"_follow_ikHandle"),sol="ikRPsolver",sj=(rollJointList[2]+"_follow"),ee=(rollJointList[2]+"_follow_tip"))
	
	#now move it to the fibula and parent it too
	cmds.parent((limbName+"_follow_ikHandle"),jointHierarchy[1])
	cmds.matchTransform((limbName+"_follow_ikHandle"),jointHierarchy[1])
	cmds.setAttr((limbName+"_follow_ikHandle.poleVectorZ"),0)
	cmds.setAttr((limbName+"_follow_ikHandle.poleVectorY"),0)
	cmds.setAttr((limbName+"_follow_ikHandle.poleVectorX"),0)
	
	#--------------------------------------------------------------------------------------------------
	#lowerLeg systems
	
	#create the aim locator which the metacarpus roll joint will always follow
	cmds.spaceLocator(n=(rollJointList[1]+"_roll_aim"))
	
	# move it to root joint and parent it to the follow joint so it moves with it 
	cmds.matchTransform((rollJointList[1]+"_roll_aim"),(rollJointList[1]+"_roll"))
	cmds.parent((rollJointList[1]+"_roll_aim"),jointHierarchy[3])
	
	#move the locator out too
	cmds.move(0,0,-5*flipSide,(rollJointList[1]+"_roll_aim"),r=1,os=1,wd=1)
	
	#make the root joint aim at the joint
	cmds.aimConstraint(jointHierarchy[2],(rollJointList[1]+"_roll"),w=1,aim=(0,1,0),u=(1,0,0),wut="object",wuo=(rollJointList[1]+"_roll_aim"),mo=1)
	
	#updated the hierarchy,parenting te follow joints to the main group
	cmds.parent((rollJointList[0]+"_follow"),(limbName+"_Grp"))

	# ------------------------------------------------------------------------------------------------
	#  head ctrls setup
	# ________________________________________________________________________________________________

	cmds.parentConstraint("head_Ctrl", "headJA_JNT", w=1, mo=1)

	# calling tail and spine modules
	dynamicsModuleSetup("tail")
	spineModule(whichSide)
	earModuleSimpleFk("l_ear")
	earModuleSimpleFk("r_ear")
	neck_SpilineSetup()

	cmds.parentConstraint("lower_spine_Ctrl", (whichSide + "legJA_JNT_FK_Ctrl_GRP"), w=1, mo=1)
	cmds.setAttr((limbName+"_Grp.visibility"),0)

	cmds.select(cl=1)
	
def neck_SpilineSetup():
	#----------------------------------------------------------------------------------------------------
	##			neck Spline Setup
	#----------------------------------------------------------------------------------------------------
	
	t="neck"
	#creating the curve 
	l=cmds.select("neckJ*_JNT")
	sel =cmds.ls(sl=True)
	sel.append("headJA_JNT")
	le= len(sel)
	positions = [cmds.xform(obj, q=True, ws=True, translation=True) for obj in sel]

	#creating ik spline handle 
	handle=cmds.ikHandle(n=("neck_ikHandle"),sol="ikSplineSolver",sj=sel[0],ee=sel[le-1],tws="easeInOut",ccv=True,scv=False,pcv=False)[0]
	my_curve = cmds.rename("curve1", "neck_curve")

	#creating extra Ctrljoint
	join=(sel[0],sel[le/2],sel[le-1])
	cmds.select(cl=1)
	for i in range(len(join)):
		jo=cmds.joint(n=join[i]+"ctrlJoint")
		cmds.matchTransform(jo,join[i])
		cmds.select(cl=1)
		
	joints = cmds.ls("neck*ctrlJoint")
	joints.append("headJA_JNTctrlJoint") 
	
	cmds.skinCluster ("neck_curve",joints)
	
	#parent constrainting 
	cmds.parentConstraint("neck_Ctrl","neckJD_JNTctrlJoint",w=1,mo=1)
	cmds.parentConstraint("head_Ctrl","headJA_JNTctrlJoint",w=1,mo=1)
	cmds.parentConstraint("upper_spine_Ctrl","neckJA_JNTctrlJoint",w=1,mo=1)
	
	cmds.group(my_curve,handle,joints,n=t+"_Setup_Grp")
	#---------------------------------------------------------------------------------------------------
	# stretchy neck setup
	#---------------------------------------------------------------------------------------------------
	
	obj= cmds.ls("neck_curve")
	rel=cmds.listRelatives(obj,s=1)[0]
	
	#create curveinfonode
	curveIn=cmds.shadingNode("curveInfo", au=1, n="neck_curve_curveInfo")
	cmds.connectAttr((rel+".worldSpace[0]"),(curveIn+".inputCurve"),f=1)
	cmds.shadingNode("multiplyDivide",au=1,n=(curveIn+"_stretch"))
	cmds.setAttr((curveIn+"_stretch.operation"),2)
	length=cmds.getAttr( "neck_curve_curveInfo.arcLength")
	cmds.setAttr((curveIn+"_stretch.input2X"),length)
	
	# connect the attr to input1
	cmds.connectAttr((curveIn+".arcLength"),(curveIn+"_stretch.input1X"),f=1)
	sel.pop()
	
	#popping the last joint of the main join list
	for i in range(len(sel)):
		cmds.connectAttr((curveIn+"_stretch.outputX"),(sel[i]+".scale.scaleX"),f=1)

	#parenting the neck ctrl with the head and upper spine controls so the neck maintains the centre
	cmds.parentConstraint("upper_spine_Ctrl","head_Ctrl","neck_Ctrl_GRP",w=1,mo=1)

def earModuleSimpleFk(Module):

	# ------------------------------------------------------------------------------------------------
	#  tail ctrls setup
	# ________________________________________________________________________________________________

	module = Module
	earJoint = cmds.ls(module+"*_JNT")

	###-----------------------------------------------------------------------------------
	###			Setup FK_Ctrls tails
	###-----------------------------------------------------------------------------------
	# connect the fk controls to the new fk joint chains

	for i in range(len(earJoint)):
		cmds.parentConstraint((earJoint[i] + "_FK_Ctrl"), earJoint[i] , w=1, mo=1)

def arbitraryControls(Module):

	# ------------------------------------------------------------------------------------------------
	#  tail ctrls setup
	# ________________________________________________________________________________________________
	'''
	module = Module
	arbJoint = cmds.ls(module+"*_JNT")
	for i in range(len(arbJoint)):
		cmds.parentConstraint((arbJoint[i] + "_FK_Ctrl"), arbJoint[i] , w=1, mo=1)
'''
	
def dynamicsModuleSetup(module):
	#------------------------------------------------------------------------------------------------
	#  tail ctrls setup 
	#________________________________________________________________________________________________
	module= module
	set=(module+"JA_JNT")
	newJointList=["_fk","_ik","_stretch"]
	jointHierarchy1= cmds.ls(module+"*_JNT")
	chainJoints=len(jointHierarchy1)

	# build the joints for tail 
	for newJoint in newJointList:
		for i in range(chainJoints):
			newJointName = jointHierarchy1[i]+newJoint

			cmds.joint(n=newJointName)
			cmds.matchTransform(newJointName,jointHierarchy1[i])
			cmds.makeIdentity(newJointName,a=1, t=0,r=1,s=0)
			
		cmds.select(cl=1)
		
	#___________________________________________________________________________________
	#controls the main joint the ik and fk joints so we can blend between both ik and fk
	for i in range(chainJoints):
		cmds.parentConstraint((jointHierarchy1[i]+"_fk"),(jointHierarchy1[i]+"_ik"),jointHierarchy1[i],w=1,mo=0)

	#making a group for tail new chains
	cmds.group((set + newJointList[0]), (set + newJointList[1]), (set + newJointList[2]), n=(module + "_NewChain_Grp"))
	cmds.setAttr((module + "_NewChain_Grp.visibility"),0)

	###-----------------------------------------------------------------------------------
	###			Setup FK_Ctrls tails
	###-----------------------------------------------------------------------------------
	# connect the fk controls to the new fk joint chains

	for i in range(chainJoints):
		cmds.parentConstraint((jointHierarchy1[i] + "_FK_Ctrl"), (jointHierarchy1[i] + "_fk"), w=1, mo=1)

	###-----------------------------------------------------------------------------------
	###			Setup IK_Ctrls tails
	###-----------------------------------------------------------------------------------

	#creating the curve 
	cmds.select(module+"*_JNT")
	sel =cmds.ls(sl=True)
	le= len(sel)
	 
	curve_degree = 3 # cubic curve1
	positions = [cmds.xform(obj, q=True, ws=True, translation=True) for obj in sel]

	my_curve = cmds.curve(d=curve_degree, p=positions,n=(module+"_curve"))
	#duplicating the above curve
	cmds.duplicate(my_curve,n=(module+"_base_dynamic_curve"))

	#creating ik spline handle 
	sele=cmds.ls((module+"*_JNT_ik"))
	cmds.ikHandle(n=(module+"_ikHandle"),sol="ikSplineSolver",sj=sele[0],ee=sele[le-1],c=(module+"_curve"),ccv=False,scv=False,pcv=False)

	#creating extra Ctrljoint
	join=(sele[0],sele[4],sele[le-1])
	cmds.select(cl=1)
	for i in range(len(join)):
		jo=cmds.joint(n=join[i]+"ctrlJoint")
		cmds.matchTransform(jo,join[i])
		cmds.select(cl=1)
	
	joints = cmds.ls(module+"*ctrlJoint")
	
	cmds.skinCluster ((module+"_curve"),joints)
	
	#adding the control 
	cmds.parentConstraint((module+"_mid_ik_Ctrl"),(module+"JE_JNT_ikctrlJoint"),w=1,mo=1)
	cmds.parentConstraint((module+"_End_ik_Ctrl"),(module+"JK_JNT_ikctrlJoint"),w=1,mo=1)
	
	#---------------------------------------------------------------------------------------
	#add the ik fk blending
	ikfkSwitch= (module+"_Switch_Ctrl")

	reverse = cmds.shadingNode("reverse", au=1, n=(module + "_Switch_Ctrl_reverse"))

	for i in range(le):
		
		getContraint=cmds.listConnections(sel[i],type="parentConstraint")[0]
		getWeights=cmds.parentConstraint(getContraint,q=1,wal=1)
		
		#adding the ik_fkSwitch
	
		cmds.connectAttr((ikfkSwitch+".ik_fk_Switch"),(getContraint+"."+getWeights[1]),f=1)
		cmds.connectAttr((module+"_Switch_Ctrl_reverse.outputX"),(getContraint+"."+getWeights[0]),f=1)
	
	cmds.connectAttr((module+"_End_ik_Ctrl.rotateY"),(module+"_ikHandle.twist"),f=1)
	
	#---------------------------------------------------------------------------------------------------
	# stretchy Spline tail setup
	#---------------------------------------------------------------------------------------------------

	obj= cmds.ls(module+"_curve")
	rel=cmds.listRelatives(obj,s=1)[0]
	
	#create curveinfonode
	curveIn=cmds.shadingNode("curveInfo", au=1, n=(module+"_curve_curveInfo"))
	cmds.connectAttr((rel+".worldSpace[0]"),(curveIn+".inputCurve"),f=1)
	cmds.shadingNode("multiplyDivide",au=1,n=(curveIn+"_stretch"))
	cmds.setAttr((curveIn+"_stretch.operation"),2)
	length=cmds.getAttr((module+"_curve_curveInfo.arcLength"))
	cmds.setAttr((curveIn+"_stretch.input2X"),length)
	# connect the attr to input1
	cmds.connectAttr((curveIn+".arcLength"),(curveIn+"_stretch.input1X"),f=1)
			
	#blendColors shading node for blending the scale from
	blendNode=cmds.shadingNode("blendColors",au=1,n=(module+"_stretch_bColors"))
	cmds.connectAttr((module+"_Switch_Ctrl.ik_fk_Switch"),(blendNode+".blender"),f=1)
	cmds.connectAttr((module+"_curve_curveInfo_stretch.outputX"),(blendNode+".color1R"),f=1)
	
	# scale connections with 
	for i in range(len(sel)):
		cmds.connectAttr((curveIn+"_stretch.outputX"),(sel[i]+"_ik.scale.scaleX"),f=1)
		cmds.connectAttr((blendNode+".outputR"),(sel[i]+".scale.scaleX"),f=1)
		
		
	#####----------------------------------------------------------------------------------------
	#####						Make dynamic setup 
	#####----------------------------------------------------------------------------------------
	
	#selecting the dynamic curve and setting up 
	grp=cmds.group( em=True, name='dynamics_Grp' )
	cmds.select("*_base_dynamic_curve")
	pm.eval('MakeCurvesDynamic')
	cmds.select("curve1")
	cmds.rename(module+"_dynamic_curve")

	cmds.select("follicle1")
	cmds.rename(module+"_follicle")
	cmds.parent("*_dynamic_curve",(module+"_follicle"),grp)
	cmds.delete("hairSystem1Follicles","hairSystem1OutputCurves")
	
	#changing the point lock change to be 
	cmds.setAttr((module+"_follicleShape.pointLock"),1)
	cmds.select((module+"_dynamic_curve"),(module+"_curve"))

	#select and create the cluster on each tail base dynamic curve points and parent them under the the dynamics ctrls
	dyn=cmds.ls(module+"*_JNT_Dyn_Ctrl")
	l= (len(dyn))

	for i in range(len(dyn)):
		cmds.select((module+"_base_dynamic_curve.cv"+str([i])))
		cmds.cluster(n=(dyn[i]+"cluster"))
		cmds.setAttr((dyn[i]+"clusterHandle.visibility"),0)
		cmds.parent((dyn[i]+"clusterHandle"),dyn[i])

	#added the blendshpe from dynamic curve to ik curve 
	cmds.blendShape((module+"_dynamic_curve"),(module+"_curve"),n=(module+"_dynamic_BsShape"))
	cmds.blendShape((module+"_dynamic_BsShape"),edit=True, w=[(0,1)])

	#group the allThe hierarchy
	cmds.group(joints,n=(module + "_controlJoints_Grp"))
	cmds.group(n="Rig_Deformations_Grp")
	cmds.group(n="Rig_Setup_Grp")
	cmds.parent((module + "_controlJoints_Grp"))
	cmds.group("hairSystem1","nucleus1",(module+"_curve"),(module+"_ikHandle"),n="Dynamics_Grp", p="Rig_Setup_Grp")

	
	#adding the dynamics attribute on the main_ctrl
	cmds.select(module+"_Switch_Ctrl")
	cmds.addAttr(ln="Dynamics",at="enum",en="DYNAMICS:")
	cmds.setAttr((module+"_Switch_Ctrl.Dynamics"),e=True,cb=True)
	cmds.addAttr(ln="Enabled",at="bool",k=True)
	cmds.addAttr(ln="Simulation",at="double",min=0,max=1,dv=0,k=True)
	cmds.addAttr(ln="FollowPose",at="double",min=0,max=1,dv=0,k=True)
	cmds.addAttr(ln="Drag",at="double",min=0,max=1,dv=0,k=True)
	cmds.addAttr(ln="Turbulance",at="double",min=0,max=1,dv=0,k=True)
	cmds.addAttr(ln="Gravity", at="double", min=0, max=1, dv=0.98, k=True)
	
	cmds.connectAttr((module+"_Switch_Ctrl.Simulation"),(module+"_dynamic_BsShape.tail_dynamic_curve"),f=1)
	cmds.connectAttr((module+"_Switch_Ctrl.FollowPose"),"hairSystemShape1.startCurveAttract",f=1)
	cmds.connectAttr((module+"_Switch_Ctrl.Drag"),"hairSystemShape1.drag",f=1)
	cmds.connectAttr((module+"_Switch_Ctrl.Turbulance"),"hairSystemShape1.turbulenceStrength",f=1)
	cmds.connectAttr((module + "_Switch_Ctrl.Gravity"), "hairSystemShape1.gravity", f=1)
	cmds.connectAttr((module+"_Switch_Ctrl.Enabled"),"nucleus1.enable",f=1)

	# connecting the controls with the lowerSpine ctrls
	cmds.parentConstraint("lower_spine_Ctrl", (module+"JA_JNT_Dyn_Ctrl"), w=1, mo=1)
	cmds.parentConstraint("lower_spine_Ctrl", (module+"JA_JNT_ikctrlJoint"), w=1, mo=1)
	cmds.parentConstraint("lower_spine_Ctrl", (module+"JA_JNT_ik"), w=1, mo=1)
	cmds.parentConstraint("lower_spine_Ctrl", (module+"JA_JNT_FK_Grp"), w=1, mo=1)

	#module correct connection with dynamic system added
	condition = cmds.shadingNode("condition", au=1, n=(module + "_sim_conditon"))
	cmds.setAttr((condition+".operation"),3)
	cmds.setAttr((condition+".colorIfTrueR"),1)
	cmds.setAttr((condition + ".colorIfFalseR"),0)
	cmds.connectAttr((ikfkSwitch + ".Simulation"), (condition + ".firstTerm"), f=1)
	cmds.connectAttr((ikfkSwitch + ".ik_fk_Switch"), (condition + ".secondTerm"), f=1)
	cmds.connectAttr((ikfkSwitch + ".Simulation"), (module + "_Dyn_Ctrl_GRP.visibility"), f=1)
	plusNode = cmds.shadingNode("plusMinusAverage", au=1, n=(module + "_plusMinus"))
	cmds.setAttr((plusNode + ".operation"), 2)
	cmds.connectAttr((condition + ".outColorR"), (plusNode + ".input1D[0]"), f=1)
	cmds.connectAttr((ikfkSwitch + ".Simulation"), (plusNode + ".input1D[1]"), f=1)
	cmds.connectAttr((condition + ".outColorG"), (module + "_ik_Ctrl_GRP.visibility"), f=1)
	cmds.connectAttr((plusNode + ".output1D"), (module + "_FK_Ctrl_GRP.visibility"), f=1)

	#connecting the parent contraint with dynamic setup it will be a little different
	for i in range(len(jointHierarchy1)):
		cmds.connectAttr((plusNode + ".output1D"), (jointHierarchy1[i]+"_parentConstraint1"+"."+jointHierarchy1[i]+"_fkW0"), f=1)


def spineModule(whichSide):

	#---------------------------------------------------------------------------------------------
	#### 		spine setup
	#---------------------------------------------------------------------------------------------
	t="Spine"
	#creating the curve
	l=cmds.select("spineJ*_JNT")
	sel =cmds.ls(sl=True)
	sel.pop(0)
	le= len(sel)
	positions = [cmds.xform(obj, q=True, ws=True, translation=True) for obj in sel]
	#my_curve = cmds.curve(d=curve_degree, p=positions,n="spine_curve")

	#creating ik spline handle
	handle=cmds.ikHandle(n=("spine_ikHandle"),sol="ikSplineSolver",sj=sel[0],ee=sel[le-1],tws="easeInOut",ccv=True,scv=False,pcv=False)[0]
	my_curve=cmds.rename("curve1","spine_curve")
	#creating extra Ctrljoint
	join=(sel[0],sel[le/2],sel[le-1])
	cmds.select(cl=1)
	for i in range(len(join)):
		jo=cmds.joint(n=join[i]+"ctrlJoint")
		cmds.matchTransform(jo,join[i])
		cmds.select(cl=1)

	joints = cmds.ls("spine*ctrlJoint")

	cmds.skinCluster (my_curve,joints)

	#parent constrainting
	cmds.parentConstraint("lower_spine_Ctrl","spineJB_JNTctrlJoint",w=1,mo=1)
	cmds.parentConstraint("mid_spine_Ctrl","spineJF_JNTctrlJoint",w=1,mo=1)
	cmds.parentConstraint("upper_spine_Ctrl","spineJI__JNTctrlJoint",w=1,mo=1)
	cmds.group(my_curve,handle,joints,n=t+"_Setup_Grp")

	#---------------------------------------------------------------------------------------------------
	# stretchy Spine setup
	#---------------------------------------------------------------------------------------------------

	#cmds.ls("spine_curve")
	obj= cmds.ls("spine_curve")
	rel=cmds.listRelatives(obj,s=1)[0]

	#create curveinfonode
	curveIn=cmds.shadingNode("curveInfo", au=1, n="spine_curve_curveInfo")
	cmds.connectAttr((rel+".worldSpace[0]"),(curveIn+".inputCurve"),f=1)
	cmds.shadingNode("multiplyDivide",au=1,n=(curveIn+"_stretch"))
	cmds.setAttr((curveIn+"_stretch.operation"),2)
	length=cmds.getAttr( "spine_curve_curveInfo.arcLength")
	cmds.setAttr((curveIn+"_stretch.input2X"),length)
	# connect the attr to input1
	cmds.connectAttr((curveIn+".arcLength"),(curveIn+"_stretch.input1X"),f=1)

	#popping the last joint of the main join list
	sel.pop()

	for i in range(len(sel)):
		cmds.connectAttr((curveIn+"_stretch.outputX"),(sel[i]+".scale.scaleX"),f=1)


	#----------------------------------------------------------------------------------------------
	#scapula jnt connection with control
	#----------------------------------------------------------------------------------------------

	cmds.parentConstraint((whichSide+"scapula_Ctrl"),(whichSide+"scapulaJA_JNT"),w=1,mo=1)

	#----------------------------------------------------------------------------------------------
	# setup for hip and scapula Ctrl
	###############################################################################################

	cmds.parentConstraint("lower_spine_Ctrl",(whichSide+"rear_hip_Ctrl_GRP"),sr=["x","y","z"],w=1,mo=1)
	cmds.parentConstraint("upper_spine_Ctrl",(whichSide+"scapula_Ctrl_Grp"),sr=["x","y","z"],w=1,mo=1)

	####-----------------------------------------------------------------------------------------------
	#space switching for spine ctrls
	#__________________________________________________________________________________________________

	cmds.spaceLocator(n="middleWorldSpace_Loc")
	cmds.parent("middleWorldSpace_Loc","root_Ctrl")
	cmds.select("mid_spine_Ctrl")
	cmds.addAttr(ln='Follow',at ='enum',k=1,en="Both:Shoulder:Root:World")
	cmds.parentConstraint("lower_spine_Ctrl","upper_spine_Ctrl","middleWorldSpace_Loc","mid_spine_Ctrl_GRP",w=1,mo=1)

	cond=["follow_both","follow_shoulder","follow_root","follow_world"]
	## space switch condition nodes
	for i in range(len(cond)):
		cmds.shadingNode("condition", au=1, n=(cond[i]+"_Condition"))
		cmds.connectAttr(" mid_spine_Ctrl.Follow",(cond[i]+"_Condition.firstTerm"),f=1)
		cmds.setAttr((cond[i]+"_Condition.secondTerm"),i)

	#setting the attributes for conditions
	cmds.setAttr("follow_both_Condition.colorIfTrueR",1)
	cmds.setAttr("follow_both_Condition.colorIfTrueG",1)
	cmds.setAttr("follow_both_Condition.colorIfFalseG",0)
	cmds.setAttr("follow_both_Condition.colorIfFalseR",0)

	#setting the shoulder condition
	cmds.setAttr("follow_shoulder_Condition.colorIfTrueR",1)
	cmds.setAttr("follow_shoulder_Condition.colorIfFalseR",0)

	#setting the root condition
	cmds.setAttr("follow_root_Condition.colorIfTrueR",1)
	cmds.setAttr("follow_root_Condition.colorIfFalseR",0)

	#setting the root condition
	cmds.setAttr("follow_world_Condition.colorIfTrueR",1)
	cmds.setAttr("follow_world_Condition.colorIfFalseR",0)

	#connect the parent constrains with condition nodes
	ctr="mid_spine_Ctrl_GRP"
	cmds.connectAttr("follow_both_Condition.outColorR",(ctr+"_parentConstraint1.upper_spine_CtrlW1"),f=1)
	cmds.connectAttr("follow_both_Condition.outColorG",(ctr+"_parentConstraint1.lower_spine_CtrlW0"),f=1)
	cmds.connectAttr("follow_both_Condition.outColorB",(ctr+"_parentConstraint1.middleWorldSpace_LocW2"),f=1)

	cmds.connectAttr("follow_shoulder_Condition.outColorR","follow_both_Condition.colorIfFalseR",f=1)

	cmds.connectAttr("follow_root_Condition.outColorR","follow_both_Condition.colorIfFalseG",f=1)

	cmds.connectAttr("follow_world_Condition.outColorR","follow_both_Condition.colorIfFalseB",f=1)
