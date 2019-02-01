#12.11.2016 - Franc
#Add option for description color of the list
#TODO: add color for Plugins Name

from MenuList import MenuList

from Tools.Directories import resolveFilename, SCOPE_ACTIVE_SKIN
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaBlend

from enigma import eListboxPythonMultiContent, gFont, BT_SCALE, BT_KEEP_ASPECT_RATIO
from Tools.LoadPixmap import LoadPixmap
import skin




def PluginEntryComponent(plugin, width=440):
	if plugin.icon is None:
		png = LoadPixmap(resolveFilename(SCOPE_ACTIVE_SKIN, "icons/plugin.png"))
	else:
		png = plugin.icon
	nx, ny, nh = skin.parameters.get("PluginBrowserName",(120, 5, 25))
	dx, dy, dh = skin.parameters.get("PluginBrowserDescr",(120, 26, 17))
	ix, iy, iw, ih = skin.parameters.get("PluginBrowserIcon",(10, 5, 100, 40))
	
	getskincolor()

	return [
		plugin,
		MultiContentEntryText(pos=(nx, ny), size=(width-nx, nh), font=0, text=plugin.name),
		MultiContentEntryText(pos=(nx, dy), size=(width-dx, dh), font=1, color=int(getskincolor()), text=plugin.description,), #color=int(colorsdesc) after all convert to integer
		MultiContentEntryPixmapAlphaBlend(pos=(ix, iy), size=(iw, ih), png = png, flags = BT_SCALE | BT_KEEP_ASPECT_RATIO)
	]

def PluginCategoryComponent(name, png, width=440):
	x, y, h = skin.parameters.get("PluginBrowserDownloadName",(80, 5, 25))
	ix, iy, iw, ih = skin.parameters.get("PluginBrowserDownloadIcon",(10, 0, 60, 50))
	return [
		name,
		MultiContentEntryText(pos=(x, y), size=(width-x, h), font=0, text=name),
		MultiContentEntryPixmapAlphaBlend(pos=(ix, iy), size=(iw, ih), png = png)
	]

def PluginDownloadComponent(plugin, name, version=None, width=440):
	if plugin.icon is None:
		png = LoadPixmap(resolveFilename(SCOPE_ACTIVE_SKIN, "icons/plugin.png"))
	else:
		png = plugin.icon
	if version:
		if "+git" in version:
			# remove git "hash"
			version = "+".join(version.split("+")[:2])
		elif version.startswith('experimental-'):
			version = version[13:]
		name += "  (" + version + ")"
	x, y, h = skin.parameters.get("PluginBrowserDownloadName",(80, 5, 25))
	dx, dy, dh = skin.parameters.get("PluginBrowserDownloadDescr",(80, 26, 17))
	ix, iy, iw, ih = skin.parameters.get("PluginBrowserDownloadIcon",(10, 0, 60, 50))
	getskincolor()
	return [
		plugin,
		MultiContentEntryText(pos=(x, y), size=(width-x, h), font=0, text=name),
		 #just use colorsdesc value (global variable) in plugin download browser too for description. no need to set another parameter in skin for this. It's the same parameter.
		MultiContentEntryText(pos=(dx, dy), size=(width-dx, dh), font=1, color=int(getskincolor()), text=plugin.description),
		MultiContentEntryPixmapAlphaBlend(pos=(ix, iy), size=(iw, ih), png = png)
	]

	
def getskincolor():
	#--------------------------------------------------------------------------------------------
	#Franc
	#NOTE: Need to define default color in *decimal* mode, as in skin parameters section: 
	#ex: <parameter name="PluginBrowserColorDesc" value="943491" /> 
	colorsdesc = skin.parameters.get("PluginBrowserDescColor",(16777215)) #<---  decimal color (default white).   For converting look at here http://www.binaryhexconverter.com/hex-to-decimal-converter
	
	#convert binary to string
	colorsdesc = str(colorsdesc)
	#'cause string return brackets [] you need to cut the brackets
	colorsdesc = colorsdesc.replace("[", "")
	colorsdesc = colorsdesc.replace("]", "")
	#print colorsdesc
	return colorsdesc
	#--------------------------------------------------------------------------------------------
	
	
	

class PluginList(MenuList):
	def __init__(self, list, enableWrapAround=True):
		MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
		font = skin.fonts.get("PluginBrowser0", ("Regular", 20, 50))
		self.l.setFont(0, gFont(font[0], font[1]))
		self.l.setItemHeight(font[2])
		font = skin.fonts.get("PluginBrowser1", ("Regular", 14))
		self.l.setFont(1, gFont(font[0], font[1]))
		colorsdesc = 0
