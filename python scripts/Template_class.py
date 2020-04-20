from reportlab.platypus import BaseDocTemplate, Frame, Paragraph, NextPageTemplate, PageBreak, PageTemplate, FrameBreak, Image
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
import json
import abc
from abc import ABC, abstractmethod, ABCMeta
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.fonts import tt2ps
# from reportlab.rl_config import canvas_basefontname as _baseFontName#
from . import Header_class 
from . import Footer_class
from .Pdfgraph_class import PDFgraph
from .Dparagraph_class import DParagraph
from .Ditle_class import DTitle
from datetime import datetime
from .CreateGraphIMG_class import GraphIMG
from .Map_class import Map
import os
from PIL import Image as ImagePIL

styles = getSampleStyleSheet()

# The main class of the process. Handles the creation of the pdf report


class DPdf:

	__slots__ = ['__doc', '__template_path', 'pathToImage', 'frame_logo', 'heading_frame', 'template_obj',
				'graph_frame', 'title_frame', 'elements', 'firstPage_frame', 'firstPage_footer', 'canvas',
				'graph_description', 'content', 'name', 'images', 'map_frame', 'legend_frame',
				'min_legend_frame', 'layer_description_frame', 'content_descriptor', 'dash_id', 'report_path', 'textarea_frame']

	def __init__(self, content):
		self.__doc = None
		self.__template_path = content['template']
		self.pathToImage = None
		self.frame_logo = None
		self.heading_frame = None
		self.template_obj = None
		self.graph_frame = None
		self.title_frame = None
		self.firstPage_frame = None
		self.firstPage_footer = None
		self.elements = []
		self.graph_description = None
		self.dash_id = content['dash_id']
		self.content = content['dashboard']
		self.report_path = '/tmp/'
		self.name = str(datetime.now().date()) + '_' + str(self.dash_id) + '_' + str(datetime.timestamp(datetime.now())).replace('.', '_') + '.pdf'
		self.canvas = Canvas(self.name)
		self.images = []

	# Creates all the types of frames and sets up resources we need for creating the report
	def create(self):
		self.template_obj = json.load(open(self.__template_path))
		self.pathToImage = self.template_obj['logo'].get('path')
		self.__doc = BaseDocTemplate(self.report_path + self.name, leftMargin=self.template_obj["margins"].get('left'),
								rightMargin=self.template_obj["margins"].get('right'),
								topMargin=self.template_obj["margins"].get('top'),
								bottomMargin=self.template_obj["margins"].get('bottom'),
								showBoundary=0)
		self.heading_frame = Frame(self.__doc.leftMargin, self.__doc.height / 2,
									self.__doc.width, self.__doc.topMargin, id='header')
		self.layer_description_frame = Frame(self.__doc.leftMargin,1 * self.__doc.height - self.__doc.topMargin - 600, self.__doc.width,
									600 , id='layer')
		self.graph_frame = Frame(self.__doc.leftMargin / 2, 1 * self.__doc.height / 3 - 40, self.__doc.width + self.__doc.leftMargin,
									self.__doc.height / 2  , id='graph')
		self.map_frame = Frame(self.__doc.leftMargin, 1 * self.__doc.height / 3 - 90, self.__doc.width,
									self.__doc.height / 2  , id='map')
		self.legend_frame = Frame(self.__doc.leftMargin,1 * self.__doc.height - 250, self.__doc.width,
									80 , id='legend')
		self.textarea_frame = Frame(self.__doc.leftMargin, self.__doc.bottomMargin + 10,
									self.__doc.width, self.__doc.height / 1.5, id='textarea')
		# self.legend_frame = Frame(self.__doc.leftMargin,1 * self.__doc.height / 3 - 50, self.__doc.width,
		# 							70 , id='legend')
		self.graph_description = Frame(self.__doc.leftMargin, self.__doc.bottomMargin * 1.5, self.__doc.width,
									self.__doc.height / 3 - self.__doc.bottomMargin * 1.5 - 25, id='graph_desc')
		self.content_descriptor = Frame(self.__doc.width/2 - 70, self.__doc.bottomMargin * 1.5 + 130, 140,
									30, id='desc')
		self.title_frame = Frame(self.__doc.leftMargin, self.__doc.height - self.__doc.topMargin - 10, self.__doc.width,
									70,	id='title')
		self.firstPage_frame = Frame(self.__doc.leftMargin, self.__doc.bottomMargin * 3, self.__doc.width,
										self.__doc.bottomMargin * 2)
		self.firstPage_footer = Frame(self.__doc.leftMargin * 2, self.__doc.bottomMargin, self.__doc.width -
										self.__doc.leftMargin * 2,	50)
		self.__doc.addPageTemplates([PageTemplate(id='first_page', frames=[self.firstPage_frame, self.firstPage_footer],
										onPage= Header_class.Heading(self.__doc, self.template_obj).heading_first_page),
									PageTemplate(id='heading', frames=self.heading_frame,
										onPage= Header_class.Heading(self.__doc, self.template_obj).heading),
									PageTemplate(id='graph',
										frames=[self.title_frame, self.layer_description_frame, self.graph_frame, self.graph_description],
										onPageEnd= Header_class.Heading(self.__doc, self.template_obj).heading),
									PageTemplate(id='map',
										frames=[self.title_frame, self.layer_description_frame, self.map_frame, self.legend_frame, self.graph_description],
										onPageEnd= Header_class.Heading(self.__doc, self.template_obj).heading),
									PageTemplate(id='text',
										frames=[self.title_frame, self.layer_description_frame],
										onPageEnd= Header_class.Heading(self.__doc, self.template_obj).heading),
									PageTemplate(id='image',
										frames=[self.title_frame, self.layer_description_frame, self.map_frame],
										onPageEnd= Header_class.Heading(self.__doc, self.template_obj).heading)])

		# TODO: Add template elements
		# elements.insert(0, e)

	# Creates the first page of the report then loops through the content and acts accordingly
	def draw(self):
		graph_counter = 0
		map_counter = 0
		current_date = datetime.today().strftime('%d/%m/%Y')
		p = DParagraph(str(self.content[0]['user_title'])+' Report', 'Centred')
		p.render(self.elements)
		p = DParagraph('Date: ' + current_date, 'Centred')
		p.render(self.elements)
		self.elements.append(FrameBreak())
		p = DParagraph('Harwell'
						'G.21-25, Building R71, Rutherford Appleton Laboratory '
						'Harwell Campus, Didcot, OX11 0QX '
						'United Kingdom '
						'+44 (0) 1235 567238', 'Centred_footer')
		p.render(self.elements)
		# self.elements.append(FrameBreak())
		# self.elements.append(PageBreak())
		# content = json.load(open('content.json'))
		# gr = json.load(open('./src/reportPDF/dummy.json'))
		# print(type(self.content))
		if type(self.content) is list:
			pass
		else:
			self.content = json.loads(self.content)
		counter = 0
		for element in self.content:
			if element['type'] == 'graph':
				graph_counter = graph_counter + 1
				# for attribute in self.content[element]:
				self.elements.append(NextPageTemplate('graph'))
				g = PDFgraph(self.__doc, self.template_obj, self.elements, [element['title'],
																			element['description'],
																			element['graph_description'],
																			element['updated_at'],
																			element['label']], graph_counter)
				img = GraphIMG(element['values'], element['units'])
				timestamp = img.create()
				# g.create_graph(self.canvas, self.__doc)
				g.insert_graph_img(timestamp)
				self.images.append(timestamp)
				self.elements = g.get_elements()
				counter = counter + 1
			if element['type'] == 'map':
				map_counter = map_counter + 1
				self.elements.append(NextPageTemplate('map'))
				map_image = Map(self.__doc, self.elements, element['path'], element['title'], element['legend'],
								element['description'], element['map_description'], element['units'], element['updated_at'],
								element['map_parameters'], element['label'], map_counter)
				self.images.append(element['path'])
				self.elements = map_image.get_elements()
				imgs = map_image.get_timestamps()
				for img in imgs:
					self.images.append(img)
				counter = counter + 1
		if counter != 0:
			self.elements.append(PageBreak())
			
		for element in self.content:
			if element['type'] == 'image':
				self.elements.append(NextPageTemplate('image'))
				t = DTitle(element['title'])
				t.render(self.elements)
				self.elements.append(FrameBreak())
				p = DParagraph(element['description'], 'Normal_Justified')
				p.render(self.elements)
				self.elements.append(FrameBreak())
				img = ImagePIL.open(str(element['path']))
				w,h = img.size
				ratio = min(400/w, 320/h)
				pic = Image(str(element['path']), w*ratio, h*ratio)
				self.elements.append(pic)
				self.elements.append(PageBreak())
		for element in self.content:
			if element['type'] == 'textarea':
				self.elements.append(NextPageTemplate('text'))
				t = DTitle(element['title'])
				t.render(self.elements)
				self.elements.append(FrameBreak())
				p = DParagraph(element['description'], 'Normal_Justified')
				p.render(self.elements)
				# self.elements.append(FrameBreak())
				self.elements.append(PageBreak())
		# self.elements.append(PageBreak())
		# t = DTitle('TITLE HERE ')
		# t.render(self.elements)
		# self.elements.append(FrameBreak())
		# p = DParagraph('Graph/Map here', 'Normal')
		# p.render(self.elements)
		# self.elements.append(FrameBreak())
		# p = DParagraph('Description for above object', 'Normal')
		# p.render(self.elements)

	def return_doc(self):
		return self.__doc

	def return_template(self):
		return self.template_obj

	def render(self):
		self.__doc.build(self.elements)
		for i in range(len(self.images)):
			os.remove(self.images[i])


if __name__ == '__main__':
	elements = []
	content = json.load(open('./src/reportPDF/content.json'))
	# content = json.load(open('dummy.json'))
	pdf = DPdf('./src/reportPDF/template.json', content)
	pdf.create()
	pdf.draw()
	pdf.render()
