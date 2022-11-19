# importing the maya commands as cmds 
import maya.cmds as cmds
import Locators
import Joints
import Control


scriptName = __name__
newWindow ='ribbonCreationv1.0'
editMode = False

theList = [None, 'TwistsDef', 'SineDef', 'BendDef','WaveDef']
def guiJointTool():
	
	if cmds.window(newWindow, q=True, exists=True):
	    cmds.deleteUI(newWindow)
	
	if cmds.windowPref(newWindow, q=True, exists=True):
	    cmds.windowPref(newWindow, r=True)
	   
	size =(300,300)
	myGUI=cmds.window(newWindow,resizeToFitChildren=1,t='ribbonCreationv1.0',widthHeight=size)
	
	cmds.columnLayout(adjustableColumn= True)
	cmds.separator(height =10)
	cmds.text(myGUI)
	cmds.separator(height =10)
	
	#cmds.columnLayout()
	#cmds.radioButtonGrp('ribbons', labelArray4=['TwistRibbon', 'SineRibbon', 'BendRibbon','WaveRibbon'], numberOfRadioButtons=4 ,cc= scriptName +'.deformer_Type()')
	cmds.radioButtonGrp('ribbons', labelArray4=['TwistRibbon', 'SineRibbon', 'BendRibbon', 'WaveRibbon'],numberOfRadioButtons=4)
	cmds.checkBoxGrp( numberOfCheckBoxes=4, label='Type of deformerz:', labelArray4=['TwistRibbon', 'SineRibbon', 'BendRibbon', 'WaveRibbon'] )
	
	#, cc = deformer_Type()
	# naming options (option menu)
	name=cmds.intFieldGrp('list_length',l= 'numberOfTwistJoints' ,value1 = 5)
	
	see=cmds.button(label="creatingRig",c=press)
	
	#buttonName= cmds.button(label="creatingRig",c=rigCreation)

	# displaying Window
	cmds.showWindow()

def press(*args):

    deformer_T = cmds.radioButtonGrp('ribbons', q=True, select=True)
    #deformer_T = cmds.checkBoxGrp('ribbons', q=True, select=True)
    print theList[deformer_T]
    selects = theList[deformer_T]
    print selects
    rigCreation()
    print "control is here "
    #calling functions according to input 
    if selects == 'TwistsDef':
    	twistRibbons()
    	
    if selects== 'SineDef':
    	sineRibbons()
    	
    if selects== 'BendDef':
    	bendRibbons()	
    
    if selects== 'WaveDef':
    	waveRibbons()	
        
	

def rigCreation(*args):
	#print deformer_T
	name1=cmds.intFieldGrp('list_length',query=True,value1=True)

	list=[""]
	list_length=name1
	
	for i in range(list_length):
		list.append("spine"+str(i+1))
	
	list.pop(0)
	#print(list)
	
	listName = list
	planeLength = 45.00 
	cmds.select(all=True)
	cmds.delete()
	
	
	cmds.nurbsPlane(p=[planeLength / 2, 0, 0], ax=[0, 0, 0], w=planeLength, lr=0.1 , d=3, u=9, v=1, n='spineNurbsPlane')
	#adding line for patch U 
	cmds.setAttr ("makeNurbPlane1.patchesU",list_length)
	cmds.rotate(0, 0, 0, 'spineNurbsPlane')
	cmds.select(d=True)
	cmds.group(em=True, n='follicle_grp')
	
	for i in range(len(listName)):    
	    y = str(i + 1)
	    cmds.createNode('follicle', n='follicle' + listName[i])
	    cmds.parent('follicle' + y,'follicle_grp', s=True)
	    cmds.setAttr('follicle' + listName[i] + '.simulationMethod', 0)
	    cmds.makeIdentity('spineNurbsPlane', apply=True, t=1, r=1, s=1, n=0)
	
	    cmds.connectAttr('follicle' + listName[i] + '.outRotate', 'follicle' + y + '.rotate', f=True)
	    cmds.connectAttr('follicle' + listName[i] + '.outTranslate', 'follicle' + y + '.translate')
	    cmds.connectAttr('spineNurbsPlaneShape.worldMatrix', 'follicle' + listName[i] + '.inputWorldMatrix')
	    cmds.connectAttr('spineNurbsPlaneShape.local', 'follicle' + listName[i] + '.inputSurface')
	
	    cmds.setAttr('follicle' + y + '.parameterV', 0.5)
	    cmds.setAttr('follicle' + y + '.parameterU', float(i) / (len(listName) - 1))
	    
	    j=cmds.joint( n= 'bind_'+listName[i]+"_JNT",p=(0, 0, 0) )
	    cmds.setAttr( j+'.translateX',0)
	    
	    #cmds.duplicate(('bind_'+listName[i+4]+"_JNT"),) cmds.ls( 'group*', sl=True )
	jntNames= cmds.ls('bind_spine*_JNT')
	sizeJntName=len(jntNames)
	middleJoint=jntNames[(sizeJntName-1)/2]
	cmds.duplicate( jntNames[0],middleJoint,jntNames[sizeJntName-1],n="spine")
	p=cmds.parent('spine','spine1','spine2',w=1)

	cmds.skinCluster(p,'spineNurbsPlane')
	for i in p: #range(len(listName))
		var = cmds.xform(i, q=1, piv=1, ws=1)
		var1 = cmds.circle (o=1,c =(var[0],var[1],var[2]),r=10,ch=0,n=(i+"_Ctrl"))
		cmds.parent(i,var1)
		#print var1
		resetPivots(var1)
	"""
	if x==1:
		twist=twistRibbons()
	"""
	#print twist
	#sine=sineRibbons()
	#print (sine)
	#cmds.reorderDeformers("skinCluster1","deform_BS","spineNurbsPlane")
	

def twistRibbons():
	dup=cmds.duplicate('spineNurbsPlane',n ='twistRibbon')
	unlockAllAttrbutes(dup)
	blendDeformer(dup)
	cmds.select(dup)
	cmds.nonLinear(type= 'Twist',ap=1)
	#print (str(dup))
	return dup
	#setAttr "Twist1Handle.rotateZ" 90;

def sineRibbons():
	dup=cmds.duplicate('spineNurbsPlane',n ='sineRibbon')
	unlockAllAttrbutes(dup)
	blendDeformer(dup)
	cmds.select(dup)
	cmds.nonLinear(type= 'Sine',ap=1)
	#print (str(dup))
	return dup
	#setAttr "Twist1Handle.rotateZ" 90;


def bendRibbons():
	dup=cmds.duplicate('spineNurbsPlane',n ='bendRibbon')
	unlockAllAttrbutes(dup)
	blendDeformer(dup)
	cmds.select(dup)
	cmds.nonLinear(type= 'Bend',ap=1)
	#print (str(dup))
	return dup
	#setAttr "Twist1Handle.rotateZ" 90;

def waveRibbons():
	dup=cmds.duplicate('spineNurbsPlane',n ='waveRibbon')
	unlockAllAttrbutes(dup)
	blendDeformer(dup)
	cmds.select(dup)
	cmds.nonLinear(type= 'Wave',ap=1)
	#print (str(dup))
	return dup
	#setAttr "Twist1Handle.rotateZ" 90;

def unlockAllAttrbutes(unlockmesh):
	objs =unlockmesh
	
	axis = ['x', 'y', 'z']
	attrs = ['t', 'r', 's']
	
	for ax in axis:
		for attr in attrs:
			for obj in objs:
				cmds.setAttr(obj+'.'+attr+ax,lock=0)

def resetPivots(var1):
    sel = var1
    for obj in sel:
        cmds.xform(obj, centerPivots = True)
        

def blendDeformer(dup):
	#if(deform_BS)
	cmds.blendShape(('*Ribbon','spineNurbsPlane'),foc =1,n='deform_BS',wc=1)
	#cmds.setAttr
