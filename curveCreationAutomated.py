import maya.cmds as cmds
import maya.mel as mm

def ribbonGuiTools():
	newWindow ="ToolsRibbon"
	if cmds.window(newWindow, q=True, exists=True):
		cmds.deleteUI(newWindow)
	if cmds.windowPref(newWindow, q=True, exists=True):
		cmds.windowPref(newWindow, r=True)
	size =(100,100)
	cmds.window(newWindow,resizeToFitChildren=1,t='ToolsRibbon',widthHeight=size)
	cmds.columnLayout(adjustableColumn=True)
	cmds.separator(height=20)
	cmds.text(l="Generate ribbonMeshes")
	cmds.separator(height=20)
	cmds.rowLayout(numberOfColumns=2,adjustableColumn=True)
	cmds.button(l="outerEdgesLoop",bgc =(1,0,0),c=outerEdgesLoop)
	cmds.button(l="innerEdgesLoop",bgc =(1,0,0),c=innerOutLoop)	
	cmds.setParent("..")
	cmds.columnLayout(adjustableColumn=True)
	#cmds.rowLayout(numberOfColumns=1)
	cmds.button(l="BuildRibbonStrip",bgc =(0,0,0),command=buildribbonplane)
	cmds.separator(height =10)
	cmds.setParent("..")
	cmds.columnLayout(adjustableColumn=True)
	cmds.radioButtonGrp('ribbons', labelArray2=['TwistRibbon', 'SineRibbon'],numberOfRadioButtons=2)
	cmds.radioButtonGrp('ribbons1', labelArray2=['BendRibbon', 'WaveRibbon'],numberOfRadioButtons=2)
	#cmds.columnLayout(adjustableColumn=True)
	# naming options (option menu)
	name=cmds.intFieldGrp('list_length',l= 'numberOfTwistJoints' ,value1 = 5)
	
	see=cmds.button(label="creatingRig",c=press)
	# displaying Window
	cmds.showWindow()
	
	
def buildribbonplane(*args):
	cmds.loft("curveInner","curveOuter",n="RibbonMesh")
	#cmds.nurbsToPoly( 'RibbonMesh',n='RibbonMesh',mnd=1,ch=0,f=0,pt=1,pc=1,chr=0.9,ft=0.01,mel=0.001,d=0.1,ut=1,
					  #un=3,vt=1,vn=3,uch=0,ucr=0,cht=0.01,es=0,ntr=0,mrt=0,uss=1)
	#cmds.polyNormal("RibbonMesh",ch=1,userNormalMode=1,normalMode=0)
	#cmds.delete("loftedSurface1","curveInner","curveOuter")


def outerEdgesLoop(*args):
	cmds.select(add=1)
	curve=cmds.polyToCurve(form=2,degree=1,conformToSmoothMeshPreview=1)[0]
	cmds.rename(curve,"curveOuter")

	
def innerOutLoop(*args):
	#inner edge loop creattin
	cmds.select(add=1)
	curve=cmds.polyToCurve(form=2,degree=1,conformToSmoothMeshPreview=1)[0]
	cmds.rename(curve, "curveInner")
	
	
def press(*args):

    deformer_T = cmds.radioButtonGrp('ribbons', q=True, select=True)
    theList = [None, 'TwistsDef', 'SineDef', 'BendDef','WaveDef']
    #deformer_T = cmds.checkBoxGrp('ribbons', q=True, select=True)
    selects = theList[deformer_T]
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
		list.append("ribbon"+str(i+1))
	
	list.pop(0)
	#print(list)
	
	listName = list
	planeLength = 45.00 
	cmds.select("RibbonMesh")
	mm.eval("createHair 1 5 10 0 0 1 0 5 0 1 2 1;")
	cmds.group(em=True, n='follicle_grp')
	cmds.delete ("hairSystem1","pfxHair1","nucleus1")
	cmds.delete("curve*")
	sel1=cmds.ls("RibbonMeshFollicle*")[0:5]
	print(sel1)
	
	for i in range(len(sel1)):  
	    l=cmds.rename(sel1[i],"follicle")
	    j=cmds.joint( n= 'bind_follicle'+str(i)+"_JNT")
	    cmds.parent(j,l)
	    cmds.matchTransform(j,l)
	    cmds.makeIdentity(apply=1,t=1,r=1,pn=1)
	    cmds.setAttr((j+".radius"),0.05)
	  
	
	cmds.delete("follicle_grp")
	cmds.rename("hairSystem1Follicles","follicle_grp")
	jntNames= cmds.ls('bind_follicle*_JNT')
	sizeJntName=len(jntNames)
	print (sizeJntName)
	middleJoint=jntNames[(sizeJntName-1)/2]
	cmds.duplicate( jntNames[0],middleJoint,jntNames[sizeJntName-1],n="ribbonBind")
	p=cmds.parent('ribbonBind','ribbonBind1','ribbonBind2',w=1)

	cmds.skinCluster(p,'RibbonMesh')
	for i in p: #range(len(listName))
		var = cmds.xform(i, q=1, piv=1, ws=1)
		var1 = cmds.circle (o=1,c =(var[0],var[1],var[2]),r=0.2,ch=0,n=(i+"_Ctrl"))
		cmds.parent(i,var1)
		#print var1
		resetPivots(var1)
	"""
	if x==1:
		twist=twistRibbons()
	"""



def twistRibbons():
	dup=cmds.duplicate('RibbonMesh',n ='twistRibbon')
	unlockAllAttrbutes(dup)
	blendDeformer(dup)
	cmds.select(dup)
	defo=cmds.nonLinear(type= 'Twist',ap=1)
	#cmds.setAttr((defo+""))
	#print (str(dup))
	return dup
	#setAttr "Twist1Handle.rotateZ" 90;

def sineRibbons():
	dup=cmds.duplicate('RibbonMesh',n ='sineRibbon')
	unlockAllAttrbutes(dup)
	blendDeformer(dup)
	cmds.select(dup)
	cmds.nonLinear(type= 'Sine',ap=1)
	#print (str(dup))
	return dup
	#setAttr "Twist1Handle.rotateZ" 90;


def bendRibbons():
	dup=cmds.duplicate('RibbonMesh',n ='bendRibbon')
	unlockAllAttrbutes(dup)
	blendDeformer(dup)
	cmds.select(dup)
	cmds.nonLinear(type= 'Bend',ap=1)
	#print (str(dup))
	return dup
	#setAttr "Twist1Handle.rotateZ" 90;

def waveRibbons():
	dup=cmds.duplicate('RibbonMesh',n ='waveRibbon')
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
	cmds.blendShape(('*Ribbon','RibbonMesh'),foc =1,n='deform_BS')
	#cmds.setAttr
	

