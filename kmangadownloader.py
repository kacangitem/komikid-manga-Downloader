#!/usr/bin/env python
# Dibuat oleh: Imam Omar Mochtar / kacangitem
# Lisensi : GPLV2
import re, sys,glob, os
from urllib import FancyURLopener
from BeautifulSoup import BeautifulSoup
from zipfile import ZipFile
from optparse import OptionParser
from urlparse import urljoin

URL_BASE = 'http://komikid.com'
PARS_VALUE = re.compile(r'value="(\w+)"')
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.1 (KHTML, like Gecko) Ubuntu/11.10 Chromium/14.0.835.202 Chrome/14.0.835.202 Safari/535.1'

class DonDown(FancyURLopener):
    version = UA

akamaru = DonDown()

def get_page_soup(url):
    """Parsing HTML yang didapat menggunakan BeautifulSoup"""
    akamaru.retrieve(url, "page.html")
    html = ""
    with open("page.html") as html_file:
        for line in html_file:
            html += line
    os.remove('page.html')
    return BeautifulSoup(html)

def get_all_chapter(soup):
    """Cari list chapter dari manga yang didapatkan"""
    links = soup.findAll('select', {"name": "chapter"})
    chapters = PARS_VALUE.findall(str(links))
    return list(set(chapters))

def getMaxPage(soup):
    """Parsing html untuk mendapatkan max halaman pada suatu chapter"""
    pages = soup.findAll('select', {"name": "page"})[0]
    balikin = PARS_VALUE.findall(str(pages))[-1]
    return balikin
    
def getPicUrl(soup):
    """Cari gambar"""
    gambar = URL_BASE+'/'+soup.findAll('img',{'class':'picture'})[0]['src'].encode()
    return gambar

def nextPage(soup):
    """Cari Halaman Selanjutnya"""
    lanjut = URL_BASE+'/'+soup.findAll('a')[4]['href'].encode()
    return lanjut

def makecbz(manga,chapter,tampung):
    """Convert gambar-gambar yang sudah diunduh menjadi cbz(zip)"""
    zipname = manga + '_' + chapter+ '.cbz'
    myzip = ZipFile(zipname, 'w')
    for filename in tampung:
        myzip.write(filename)
        os.remove(filename)
    myzip.close()

def DownPic(list_url,manga,chapter):
    """Download gambar dari hasil parsing html"""
    tampung = []
    now = 1
    tot = len(list_url)
    print 'Mengunduh {0} chapter {1} ...'.format(manga,chapter)
    for url in list_url:
        progBar(now,tot)
        file = url.split('/')[-1]
        akamaru.retrieve(url,file)
        tampung.append(file)
        now += 1
    makecbz(manga,chapter,tampung)
    
def progBar(now,total):
    """Progressbar masih ancur"""
    bar = total
    percent = '%d%%' % int(round(float((now * 100.0) / total)))
    prog = '['+'=' * now +'>'+ ' ' * (bar - now)  +']'+ percent
    if sys.platform.lower().startswith('win'):
        print prog, '\r',
    else:
        print prog,chr(27) + '[A'

def list_dwn_pic(first_url,manga,chapter):
    """Listing gambar yang akan diunduh dari hasil parsing HTML"""
    soup = get_page_soup(first_url+'/'+chapter)
    max = getMaxPage(soup)
    picurl = []
    for seq in xrange(int(max)):
        picture = getPicUrl(soup)
        picurl.append(picture)
        next = nextPage(soup)
        soup = get_page_soup(next)
    DownPic(picurl,manga,chapter)
    
def contoh():
    print "Contoh penggunaan:"
    print "1. Download semua chapter pada manga Naruto"
    print "     kmanga.py -m Naruto"
    print "2. Download chapter hanya chapter 500"
    print "     kmanga.py -m Naruto -c 500"
    print "3. Download chapter dari 500 hingga 550"
    print "     kmanga.py -m Naruto -c 500-550"
    print "4. Download chapter terbaru"
    print "     kmanga.py -m Naruto -t"
 
def DownMe(manga,chapterMin=None,chapterMax=None,newchap=False):
    """Kandang Macan"""
    manga_url = urljoin(URL_BASE,manga)
    print manga_url
    bubur = get_page_soup(manga_url)
    bab = sorted(  get_all_chapter(bubur) )

    if chapterMin:
        if chapterMin not in bab:
            print 'manga {0} chapter {1} tidak tersedia !!!'.format(manga,chapterMin)
            sys.exit(1)

    if chapterMax:
        if chapterMax not in bab:
            print 'manga {0} chapter {1} tidak tersedia !!!'.format(manga,chapterMax)
            sys.exit(1)
                       
    if chapterMin and chapterMax:
        for chapter in xrange(int(chapterMin),int(chapterMax)+1):
            list_dwn_pic(manga_url,manga,str(chapter))
            
    elif chapterMin:
        list_dwn_pic(manga_url,manga,str(chapterMin))
        
    elif newchap:
		if len(bab) == 0:
			print '{0} tidak tersedia, Pastikan url diatas adalah manga yang dimaksud pada {1} !!'.format(manga,URL_BASE)
			sys.exit(1)
		else:
			list_dwn_pic(manga_url,manga,str(bab[-1]))
    else:
        for bba in bab:
            list_dwn_pic(manga_url,manga,str(bba))

if __name__ ==  '__main__':
    pars = OptionParser()
    pars.add_option('-m','--manga',action='store', default=None,\
    dest='manga',help='Manga yang akan diunduh, nama manga harus sama dengan URL pada komikid.com')
    pars.add_option('-c','--chapter',action='store',default=None,\
    dest='chapter',help='Pilih Manga yang akan diunduh, dapat menggunakan range untuk mengunduh banyak manga sekaligus')
    pars.add_option('-t','--terbaru',action='store_true',default=False,\
    dest='terbaru',help='Download chapter terbaru dari manga yang dipilih')

    if len(sys.argv) == 1:
        pars.print_help()
        contoh()
        sys.exit(1)

    option, remain= pars.parse_args(sys.argv[1:])
    if not option.manga and option.chapter :
        print "Anda harus menyertakan nama manga yang akan diunduh !!!!"
        sys.exit(1)

    if not option.manga and  option.terbaru:
        print "Anda harus menyertakan nama manga yang akan diunduh !!!!"
        sys.exit(1)
    if option.chapter and option.terbaru:
        print "Opsi mengunduh manga terbaru tidak bisa dibarengi dengan opsi chapter !!!"
        sys.exit(1)

    if option.manga and not option.chapter and not option.terbaru:
        DownMe(option.manga)

    elif option.manga and option.chapter:
        if '-' in option.chapter:
            setmin,setmax = option.chapter.split('-')
            DownMe(option.manga,setmin,setmax)
        else:
            DownMe(option.manga,option.chapter)
            
    elif option.manga and option.terbaru:
        DownMe(option.manga,newchap=option.terbaru)
