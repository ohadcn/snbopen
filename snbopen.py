#!/usr/bin/python


from zipfile import ZipFile
from xml.dom.minidom import parseString
from zlib import decompress
import Image
from os import system,sep
from sys import argv
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.pdfbase.pdfutils import ImageReader
from re import sub
from tempfile import gettempdir
import webbrowser

def showUsage():
	print """
	Usage: snbopen snbfile [pdffile]
		snbopen opens .snb files created by samsung tablets
		if pdf file is specified the program converts the snb file to the pdf.
	"""

def zipRead(zipFile,filename):
	tempFile = zipFile.open(filename)
	str = tempFile.read()
	tempFile.close()
	return str

def addImage(snbFile,canvas,image,rels,element):
	imgFileName = "snote/"+rels[image.getAttribute("r:id")]
	imgStr = zipRead(snbFile,imgFileName)
	if imgFileName.endswith(".zdib"):
		imgStr = decompress(imgStr)
		width = ord(imgStr[5]) * 256 + ord(imgStr[4])
		height = ord(imgStr[9]) * 256 + ord(imgStr[8])
		img = Image.fromstring("RGBA",(width,height),imgStr[52:])
		canvas.drawInlineImage(alpha_to_color(img),0,0,595.27,841.89)
	else:
		style = imagePoss(element.getElementsByTagName("v:shape")[0].getAttribute("style"))
		img=Image.open(BytesIO(imgStr))
		canvas.drawInlineImage(img,style.left,style.bottom,style.width,style.height)


def addText(canvas,element,styles):
	for run in element.getElementsByTagName("sn:r"):
		if(len(run.getElementsByTagName("sn:t")) > 0):
			##TODO: support italic, bold and underlined text
			charStyle = styles["Character" + run.getAttributeNode("sn:rStyle").value]
			text=run.getElementsByTagName("sn:t")[0].firstChild.nodeValue
			canvas.setFont("Helvetica",charStyle.size)
			canvas.setFillColor(charStyle.color)
			canvas.drawString(40,810-charStyle.size,text)
			##TODO: support non-unicode characters


def readRelsFile(snbFile):
	relations = parseString(zipRead(snbFile,"snote/_rels/snote.xml.rels"))
	rels=dict()
	for relation in relations.getElementsByTagName("Relationship"):
		rels[relation.getAttribute("Id")] = relation.getAttribute("Target")
	return rels


def readCharStyles(snbFile):
	styles = parseString(zipRead(snbFile,"snote/styles.xml"))
	charStyles = dict()
	for style in styles.getElementsByTagName("sn:style"):
		if style.getAttributeNode("sn:type").value == "character":
			if len(style.getElementsByTagName("sn:color"))>0:
				color = style.getElementsByTagName("sn:color")[0].getAttribute("sn:val")
			else:
				color = "000000"
			if len(style.getElementsByTagName("sn:sz"))>0:
				size = int(style.getElementsByTagName("sn:sz")[0].getAttribute("sn:val"))*.5
			else:
				size = 16
			charStyles[style.getAttribute("sn:styleId")] = Style(len(style.getElementsByTagName("sn:b"))>0,
				len(style.getElementsByTagName("sn:i"))>0, len(style.getElementsByTagName("sn:u"))>0,color,size)
	return charStyles


class Style:
	def __init__(self, bold, italic, underline,color="000000",size=48):
		self.bold = bold
		self.italic = italic
		self.underline = underline
		self.color = "0X"+color
		self.size=size


class imagePoss:
	def __init__(self,style):
		info = sub(r'[A-Za-z\-:]',"",style).split(";")
		self.left=float(info[2])
		self.bottom=841.89 -(float(info[3])+float(info[5]))
		self.width = float(info[4])
		self.height = float(info[5])


def alpha_to_color(image, color=(255, 255, 255)):
    image.load()  # needed for split()
    background = Image.new('RGB', image.size, color)
    background.paste(image, mask=image.split()[3])  # 3 is the alpha channel
    return background


def snbToPdf(snbname,pdfname = None ):
	snbFile=ZipFile(snbname,"r")

	rels = readRelsFile(snbFile)
	charStyles = readCharStyles(snbFile)

	snote = parseString(zipRead(snbFile,"snote/snote.xml"))
	bodyElements=snote.firstChild.firstChild.childNodes
	for element in bodyElements:
		if element.nodeName=="sn:page":
			if 'pdfCanvas' in vars():
				pdfCanvas.showPage()
			else:
				pdfCanvas = canvas.Canvas(pdfname if pdfname else snbname.replace(".snb",".pdf"))

		#ussually images
		elif element.nodeName == "sn:SNoteObj":
			images=element.getElementsByTagName("v:imagedata")
			if len(images)!=0:
				addImage(snbFile,pdfCanvas,images[0],rels,element)

			else:
				print "unknown SNoteObj" +"on page "+str(pdfCanvas.getPageNumber())

		elif element.nodeName == "sn:l":
			addText(pdfCanvas,element,charStyles)

		else:
			print "unknown element type:"+element.nodeName+" on page "+str(pdfCanvas.getPageNumber())

	if(pdfname):
		pdfCanvas.save()

	snbFile.close()


if len(argv)==2:
	pdfFileName= gettempdir()+sep+sub('.*'+sep,"",argv[1]).replace(".snb",".pdf")
	snbToPdf(argv[1],pdfFileName)
	webbrowser.open(pdfFileName)
elif len (argv)==3:
	snbToPdf(argv[1],argv[2])
else:
	showUsage()