# -*- coding: utf-8 -*-
import re, os, sys
import scrapy
from scrapy.selector import Selector

from project.items import ResearcherItem

class CvLACSpider(scrapy.Spider):
    
    name = 'cvlac_spider'
    start_urls = []
    #start_urls = ['http://scienti.colciencias.gov.co:8081/cvlac/visualizador/generarCurriculoCv.do?cod_rh=0000541737']

    allowed_domains = ['scienti.minciencias.gov.co']

    def __init__(self):
        script_dir = os.path.dirname(__file__)
        with open(os.path.join(script_dir, "urls.txt"), "r") as f:
            self.start_urls = f.readlines()


    def parse(self, response):

        personal = self.personal_info(response)

        if True:

            areas = self.research_area_info(response)
            academic_records = self.academic_records(response)
            additional_training =  self.additional_training(response)
            jobs = self.job_records(response)
            languages = self.languages(response)
            research_lines = self.research_lines(response)
            awards = self.awards(response)
            cientific_events = self.cientific_events(response)
            cientific_papers = self.cientific_papers(response)
            books = self.books(response)
            software = self.software_records(response)
            academic_projects = self.academic_projects(response)

            res = ResearcherItem()

            res["personal_info"]= personal
            res["research_area_info"]= areas
            res["academic_studies"]= academic_records
            res["additional_training"]= additional_training
            res["jobs"]= jobs
            res["languages"]= languages
            res["research_lines"]= research_lines
            res["awards"]= awards
            res["cientific_events"]= cientific_events
            res["cientific_papers"]= cientific_papers
            res["books"]= books
            res["software"]= software
            res["academic_projects"]= academic_projects


            yield res

    
    def personal_info(self, response):

        item = {}

        content = response.xpath("//td[a[@name='datos_generales']]")
        cols = content.xpath('table//tr//td//text()').extract()
        cols = [ ' '.join(x.split()) for x in cols ]

        if not cols:
            content = response.xpath("//blockquote[a[@name='datos_generales']]")
            cols = content.xpath('table//tr//td//text()').extract()
            cols = [ ' '.join(x.split()) for x in cols ]
            item["is_cv_public"] = "False"
        else:
            item["is_cv_public"] = "True"


        url = response.url
        cv_id = url[ url.index('=')+1 : ]

        cate_index = cols.index('Categoría') if 'Categoría' in cols else -1  
        category = cols[cate_index+1] if cate_index >= 0 else "No indica"

        name_index = cols.index('Nombre') if 'Nombre' in cols else -1  
        name = cols[name_index+1] if name_index >= 0 else "No indica"

        cit_index = cols.index('Nombre en citaciones') if 'Nombre en citaciones' in cols else -1  
        citation_name = cols[cit_index+1] if cit_index >= 0 else "No indica"

        nat_index = cols.index('Nacionalidad') if 'Nacionalidad' in cols else -1  
        nationality = cols[nat_index+1] if nat_index >= 0 else "No indica"

        gen_index = cols.index('Sexo') if 'Sexo' in cols else -1  
        gender = cols[gen_index+1] if gen_index >= 0 else "No indica"
        
        

        try:

            item["cv_id"] = cv_id.strip()
            item["cv_url"] = url
            item["name"] = name.strip()
            item["citation_name"] = citation_name.strip()
            item["nationality"] = nationality.strip()
            item["gender"] = gender.strip()
            item["category"] = category.strip()

        except:
            item["error"] = "error al leer"

        return item


    def research_area_info(self, response):

        content = response.xpath("//td[a[@name='otra_info_personal']]")
        cols = content.xpath('table//tr//td//li//text()').extract()
        cols = [ x.split('--') for x in cols ]

        areas = []

        for col in cols:

            area = {}

            try:
                area['main_area'] = col[0].strip()
                area['secondary_area'] = col[1].strip()
                area['specific_area'] = col[2].strip()
                areas.append(area)
            except:
                area["error"] = "Parsing error"
                areas.append(area)

        return areas


    def academic_records(self, response):

        sel = Selector(response)
        select = sel.xpath(u'//td//text()[contains(.,"Formación Académica")]/ancestor::tr[1]').xpath('following-sibling::tr')

        studies = []

        for tr in select:
            study = {}

            cols = tr.xpath('td[2]//text()').extract()

            try:
                study['level'] = cols[0].strip()
                study['institution'] = cols[1].strip()
                study['title'] = cols[2].strip()
                study['project'] = cols[4].strip()
                studies.append(study)
            except:
                study["error"] = "Parsing error"
                studies.append(study)            
        
        return studies


    def additional_training(self, response):

        sel = Selector(response)
        select = sel.xpath(u'//td//text()[contains(.,"Formación Complementaria")]/ancestor::tr[1]').xpath('following-sibling::tr')

        studies = []

        for tr in select:
            study = {}

            cols = tr.xpath('td[2]//text()').extract()


            studies.append(study)

            try:
                study['type'] = cols[0].strip()
                study['institution'] = cols[1].strip()
                study['title'] = cols[2].strip()
        
                studies.append(study)
            except:
                study["error"] = "Parsing error"
                studies.append(study)  

        
        return studies


    def job_records(self, response):

        sel = Selector(response)
        select = sel.xpath(u'//td//text()[contains(.,"Experiencia profesional")]/ancestor::tr[1]').xpath('following-sibling::tr')

        jobs = []

        for tr in select:
            job = {}
                        
            cols = tr.xpath('td[2]/strong//text()').extract()

            company = ''.join(tr.xpath('td[2]/b//text()').extract())
            
            try:
                if company.strip() !="": 
                    job['company'] = company
                    job['activity'] = tr.xpath('td[2]/*[@class="blueTitle"]//text()').extract()
                    jobs.append(job)
            except:
                job["error"] = "Parsing error"
                jobs.append(job)       
        

        return jobs


    def languages(self, response):

        sel = Selector(response)
        select = sel.xpath(u'//td//text()[contains(.,"Idiomas")]/ancestor::tr[1]').xpath('following-sibling::tr')[1:]

        languages = []

        for tr in select:
            
            lang = {}
            
            try:
                lang['name'] = ''.join(tr.xpath('td[1]//text()').extract()).strip()
                lang['speaking'] = ''.join(tr.xpath('td[2]//text()').extract()).strip()
                lang['writing'] = ''.join(tr.xpath('td[3]//text()').extract()).strip()
                lang['listening'] = ''.join(tr.xpath('td[4]//text()').extract()).strip()
                lang['understand'] = ''.join(tr.xpath('td[5]//text()').extract()).strip()

                languages.append(lang)
            except:
                lang["error"] = "Parsing error"
                languages.append(lang)


        return languages


    def research_lines(self, response):

        sel = Selector(response)
        select = sel.xpath(u'//td//text()[contains(.,"Líneas de investigación")]/ancestor::tr[1]').xpath('following-sibling::tr')

        lines = []

        for tr in select:
            
            line = {}

            try:
                line['name'] = ''.join(tr.xpath('td//text()').extract()).split(', Activa:',1)[0].strip()
                line['active'] = ''.join(tr.xpath('td//text()').extract()).split(':')[1].strip()
                lines.append(line)
            except:
                line["error"] = "Parsing error"
                lines.append(line)


        return lines


    def awards(self, response):

        sel = Selector(response)
        select = sel.xpath(u'//td//text()[contains(.,"Reconocimientos")]/ancestor::tr[1]').xpath('following-sibling::tr')

        awards = []

        for tr in select:

            resto= ' '.join(tr.xpath('td//text()').extract())
            
            reconocimiento = {}

            try:
                nombre, empresa = resto.split(',', 1)
                reconocimiento['name'] = nombre.strip()
                reconocimiento['institution'] = empresa.strip()
                awards.append(reconocimiento)
            except:
                reconocimiento["error"] = "Parsing error"
                awards.append(reconocimiento)


        return awards


    def cientific_events(self, response):

        sel = Selector(response)
        select = sel.xpath(u'//td//text()[contains(.,"Eventos científicos")]/ancestor::tr[1]').xpath('following-sibling::tr')

        events = []

        for tr in select:

            event_info =[x.strip() for x in ''.join(tr.xpath('td/table/tr[1]/td//text()').extract()).strip().split('\r\n') if x.strip()]

            event = {}

            try:
                event['name'] = event_info[0].split('Nombre del evento:')[1].strip()
                event['type'] = event_info[1].split('Tipo de evento:')[1].strip()
                event['kind'] = event_info[2].split(u'\xc1mbito:')[1].strip()
                event['presented'] = event_info[3].split('Realizado el:')[1].strip() + ' ' + event_info[4].strip()
                events.append(event)
        
            except:
                event["error"] = "Parsing error"
                events.append(event)

        return events


    def cientific_papers(self, response):

        sel = Selector(response)        
        tr_list = sel.xpath("//td[a[@name='articulos']]").xpath('table//tr[1]/following-sibling::tr')

        papers = []

        for tr1, tr2 in zip(tr_list[::2], tr_list[1::2]):

            paper = {}

            try:
                paper['type'] = ''.join(tr1.xpath('.//text()').extract()).strip().split('-')[1].strip()
                paper['published'] = ''.join(tr1.xpath('.//text()').extract()).strip().split('-')[2].strip()

                paper['title'] = ''.join(tr2.xpath('.//text()').extract()).strip().split(' En:')[0].partition('"')[-1].strip().replace('\r\n', ' ')
                
                authors = ', '.join([x.strip() for x in ''.join(tr2.xpath('.//text()').extract()).strip().split('. En:')[0].partition('"')[0].strip().replace('\r\n', ' ').split(',') if x.strip()]) 
                paper['authors'] = [x.strip() for x in authors.split(',')]             
                paper['place'] = ''.join(''.join(tr2.xpath('.//text()').extract()).strip().split('. En:')[1:]).strip().split('\r\n')[0].strip()
                paper['ident'] = ''.join(''.join(tr2.xpath('.//text()').extract()).strip().split('. En:')[1:]).strip().split('\r\n')[2].strip()
                paper['institution'] = ''.join(''.join(tr2.xpath('.//text()').extract()).strip().split('. En:')[1:]).strip().split('\r\n')[3].split(':')[-1].strip()
                
                if ''.join(tr2.xpath('.//text()').extract()).strip().find('Palabras:') != -1:
                    keywords =  ', '.join([x.strip() for x in ''.join(tr2.xpath('.//text()').extract()).strip().split('Palabras:')[-1].strip().split('Sectores:')[0].split(',') if x.strip()])
                    paper['keywords']  = [x.strip() for x in keywords.split(',')]
                else:
                    paper['keywords'] = []

                papers.append(paper)
        
            except:
                paper["error"] = "Parsing error"
                papers.append(paper)


        return papers


    def books(self, response):

        tr_list = response.xpath("//td[a[@name='libros']]").xpath('table//tr[1]/following-sibling::tr')

        books = []

        for tr1, tr2 in zip(tr_list[::2], tr_list[1::2]):

            book = {}

            try:
                book['type'] = '-'.join(''.join(tr1.xpath('.//text()').extract()).strip().split('-')[1:]).strip()
                
                book['authors'] = ', '.join([x.strip() for x in ''.join(tr2.xpath('.//text()').extract()).strip().split(' En:')[0].rsplit(',',1)[0].strip().replace('\r\n', ' ').split(',')])
                book['title'] = ''.join(tr2.xpath('.//text()').extract()).strip().split(' En:')[0].rsplit(',',1)[1].strip()
                book['place'] = ''.join(''.join(tr2.xpath('.//text()').extract()).strip().split(' En:')[1:]).strip().split('\r\n')[0].strip()
                book['isbn'] = ''.join(''.join(tr2.xpath('.//text()').extract()).strip().split(' En:')[1:]).strip().split('\r\n')[3].split(':')[-1].strip()
                book['ed'] = ''.join(''.join(tr2.xpath('.//text()').extract()).strip().split(' En:')[1:]).strip().split('\r\n')[2].split(':')[-1].strip()

                books.append(book)
        
            except:
                book["error"] = "Parsing error"
                books.append(book)


        return books


    def software_records(self, response):

        sel = Selector(response)          
        content = response.xpath("//td[a[@name='software']]").xpath('table//tr[1]/following-sibling::tr')

        software = []

        for tr1, tr2 in zip(content[::2], content[1::2]):

            soft = {}
        
            try:
                soft['type'] = '-'.join(''.join(tr1.xpath('.//text()').extract()).strip().split('-')[1:]).strip()
                soft_info = [x.strip() for x in ''.join(tr2.xpath('.//text()').extract()).strip().split(' Nombre comercial:')[0].rsplit(',',1)[0].strip().replace('\r\n', ' ').split(',')]

                soft['authors'] = soft_info[:-1]
                soft['name'] = soft_info[-1]
                software.append(soft)
        
            except:
                soft["error"] = "Parsing error"
                software.append(soft)


        return software


    def academic_projects(self, response):

        sel = Selector(response)          
        content = response.xpath("//td[a[@name='trabajos_dirigi']]").xpath('table//tr[1]/following-sibling::tr')

        projects = []

        for tr1, tr2 in zip(content[::2], content[1::2]):

            proj = {}
 
            try:
        
                proj['type'] = '-'.join(''.join(tr1.xpath('.//text()').extract()).strip().split('-')[1:]).strip()
                proj_info = ''.join(tr2.xpath('.//text()').extract()).replace('\r\n', ' ').strip()
                
                title_institution = re.sub(' +', ' ',proj_info.split(' Estado:',1)[0].strip())

                if len(title_institution.split(',',1))  > 1 :
                    title_institution = title_institution.split(',',1)[1].strip() 


                proj['title'] = title_institution.split("\xa0")[0].strip()
                proj['university'] = title_institution.split("\xa0")[-1].strip()
                
                student_role = re.sub(' +', ' ',proj_info.split(' Persona orientada:',1)[1].strip())

                students = []
                students = re.sub(' +', ' ',student_role.split(' Dirigió como:',1)[0].strip().split(',',1)[0]).strip().split(';')
                proj['students'] = students

                role = re.sub(' +', ' ',student_role.split(' Dirigió como:',1)[1].strip().split(',',1)[0]).strip()
                proj['role'] = role
                
                projects.append(proj)
        
            except:
                proj["error"] = "Parsing error"
                projects.append(proj)


        return projects