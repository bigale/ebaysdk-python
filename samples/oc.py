from temboo.Library.Amazon.Marketplace.Products import ListMatchingProducts
from temboo.Library.Amazon.Marketplace.Products import GetMatchingProduct
from temboo.Library.Amazon.Marketplace.Products import GetCompetitivePricingForASIN
from temboo.Library.Utilities.XML import GetValuesFromXML
from temboo.Library.Utilities.XML import RunXPathQuery
from temboo.core.session import TembooSession
#import os.path
#import os.listdir
import os
import glob
import codecs
import json
import csv
import pandas as pd
import sys
import base64
import xlrd
from lxml import etree
from lxml import html
import StringIO
import numpy
from xml.sax.saxutils import escape
import trading
import logging
from collections import defaultdict
import sqlite3
from dumptruck import DumpTruck
import urllib2
from bs4 import BeautifulSoup
from bs4 import NavigableString
from bs4 import UnicodeDammit
import requests
import re, htmlentitydefs
import urllib

class OC(object):
    """
    OC = OmniCommerce
    """
    def __init__(self, createAmazonSession=False, updateBodyStyleDict=False):
        # create GUI
        self.AWSMarketplaceId = "ATVPDKIKX0DER"
        self.AWSAccessKeyId = "AKIAIM72TJF6LJT6LAFA"
        self.Endpoint= "mws.amazonservices.com"
        self.AWSSecretKeyId = "fLOaCWX2cfshWxJjTNnd93BH5lyqZGUNOeOgpjJR"
        self.AWSMerchantId = "AQE7DV06HBSDG"
        self.workingGrid = pd.DataFrame()

        # Create a session with your Temboo account details
        if createAmazonSession == True:
            self.session = TembooSession("bigale", "myFirstApp", "e0beb98579754f5080e5e96ef511d0b1")

        (self.opts, self.args) = trading.init_options()
        self.logger = logger or self.logging.getLogger(__name__)

        #setup sqlite 3 as datastore and dumptruck as document-like interface
        #this will allow easy interface commands for json and xml to/from eBay
        self.ocdb = r'c:\test\ocdb.db'
        self.conn = sqlite3.connect(self.ocdb)
        self.dt = DumpTruck(self.ocdb)

        #replaced hard-coded dict with json file
        self.bodyStyle = {
        "AT": {"Name":"ADULT 18/1 - Heavier","Short Name":"18/1 SS","Material":"100% Cotton", "Style" : "Short-Sleeve Tee", "eBayStyle" : "Graphic Tee", "eBaySizeType" : "Regular", "eBayCategory" : "15687", "SizePrice" : [("S",12.00),("M",12.00),("L",12.00),("XL",12.00),("XXL",13.50),("XXXL",14.50)]},
        "SF": {"Name":"ADULT 30/1 - Lighter","Material":"100% Cotton", "Style" : "Slim Fit Tee", "eBayStyle" : "Graphic Tee", "eBaySizeType" : "Slim Fit", "eBayCategory" : "15687", "SizePrice" : [("S",13.00),("M",13.00),("L",13.00),("XL",13.00),("XXL",14.50),("XXXL",15.50)]},
        "HA": {"Name":"ADULT HEATHER","Material":"Cotton Blend", "Style" : "Short-Sleeve Tee", "eBayStyle" : "Graphic Tee", "eBaySizeType" : "Regular", "eBayCategory" : "15687", "SizePrice" : [("S",13.00),("M",13.00),("L",13.00),("XL",13.00),("XXL",14.50),("XXXL",15.50)]},
        "AV": {"Name":"ADULT VNECK","Material":"100% Cotton", "Style" : "Slim Fit V-Neck Tee", "eBayStyle" : "Graphic Tee", "eBaySizeType" : "Slim Fit", "eBayCategory" : "15687", "SizePrice" : [("S",14.00),("M",14.00),("L",14.00),("XL",14.00),("XXL",15.50),("XXXL",16.50)]},
        "TK": {"Name":"ADULT TANK TOP","Material":"100% Cotton", "Style" : "Tank Top Tee", "eBayStyle" : "Graphic Tee", "eBaySizeType" : "Regular", "eBayCategory" : "15687", "SizePrice" : [("S",13.00),("M",13.00),("L",13.00),("XL",13.00),("XXL",14.50),("XXXL",15.50)]},
        "AL": {"Name":"ADULT LONG SLEEVE","Material":"100% Cotton", "Style" : "Long-Sleeve Tee", "eBayStyle" : "Graphic Tee", "eBaySizeType" : "Regular", "eBayCategory" : "15687", "SizePrice" : [("S",15.00),("M",15.00),("L",15.00),("XL",15.00),("XXL",17.00),("XXXL",18.00)]},
        "AR": {"Name":"ADULT RINGER","Material":"100% Cotton", "Style" : "Short-Sleeve Ringer Tee", "eBayStyle" : "Graphic Tee", "eBaySizeType" : "Regular", "eBayCategory" : "15687", "SizePrice" : [("S",15.00),("M",15.00),("L",15.00),("XL",16.50),("XXL",17.50),("XXXL",18.50)]},
        "AFTH": {"Name":"ADULT PULLOVER HOODIE","Material":"Cotton Blend", "Style" : "French Terry", "eBayStyle" : "Hoodie", "eBaySizeType" : "Regular", "eBayCategory" : "155183", "SizePrice" : [("S",23.00),("M",23.00),("L",23.00),("XL",23.00),("XXL",26.00),("XXXL",29.00)]},
        "WT": {"Name":"WOMEN'S TEE","Material":"100% Cotton", "Style" : "Short-Sleeve Tee", "eBayStyle" : "Graphic Tee", "eBaySizeType" : "Regular", "eBayCategory" : "63869", "SizePrice" : [("S",13.00),("M",13.00),("L",13.00),("XL",13.00),("XXL",14.50),("XXXL",15.50)]},
        "LWT": {"Name":"WOMEN'S TEE","Material":"100% Cotton", "Style" : "Short-Sleeve Tee", "eBayStyle" : "Graphic Tee", "eBaySizeType" : "Regular", "eBayCategory" : "63869", "SizePrice" : [("S",13.00),("M",13.00),("L",13.00),("XL",13.00),("XXL",14.50),("XXXL",15.50)]},
        "JS": {"Name":"JUNIOR SHEER","Material":"100% Cotton", "Style" : "Cap-Sleeve Sheer Tee", "eBayStyle" : "Graphic Tee", "eBaySizeType" : "Slim Fit", "eBayCategory" : "175529", "SizePrice" :  [("S",13.00),("M",13.00),("L",13.00),("XL",13.00),("XXL",14.50),("XXXL",15.50)]},
        "JV": {"Name":"JUNIOR VNECK","Material":"100% Cotton", "Style" : "Cap-Sleeve Sheer V-Neck Tee", "eBayStyle" : "Graphic Tee", "eBaySizeType" : "Slim Fit", "eBayCategory" : "175529", "SizePrice" :  [("S",13.00),("M",13.00),("L",13.00),("XL",13.00),("XXL",14.50),("XXXL",15.50)]},
        "YT": {"Name":"YOUTH 18/1 COTTON","Material":"100% Cotton", "Style" : "Short-Sleeve Tee", "eBayStyle" : "Graphic Tee", "eBaySizeType" : "Regular", "eBayCategory" : "175521", "SizePrice" : [("S",11.00),("M",11.00),("L",11.00),("XL",11.00),("XXL",12.50),("XXXL",13.50)]},
        "KT": {"Name":"JUVENILE","Material":"100% Cotton", "Style" : "Short-Sleeve Tee", "eBayStyle" : "Graphic Tee", "eBaySizeType" : "Regular", "eBayCategory" : "175529", "SizePrice" : [("4",10.00),("5-6",10.00),("7",10.00)]},
        "TT": {"Name":"TODDLER","Material":"100% Cotton", "Style" : "Short-Sleeve Tee", "eBayStyle" : "Graphic Tee", "eBaySizeType" : "Regular", "eBayCategory" : "15687", "SizePrice" : [("S",10.00),("2T",10.00),("3T",10.00),("4T",10.00)]},
        "SS": {"Name":"INFANT SNAPSUIT","Material":"100% Cotton", "Style" : "Short-Sleeve Snapsuit", "eBayStyle" : "Graphic Tee", "eBaySizeType" : "Regular", "eBayCategory" : "15687", "SizePrice" : [("6",12.00),("12",12.00),("18",12.00),("24",12.00)]},
        "PT": {"Name":"ADULT PREMIUM TEE","Material":"Cotton Blend", "Style" : "Short-Sleeve Tee", "eBayStyle" : "Graphic Tee", "eBaySizeType" : "Regular", "eBayCategory" : "15687", "SizePrice" : [("S",14.00),("M",14.00),("L",14.00),("XL",14.00),("XXL",15.50),("XXXL",16.50)]}
        }
        keywordsAll = ['Tatoo Art', 'Nailhead Rhinestones', 'Design on Front and Back', 'Biker' ]
        bulletPoints = ['Eco Friendly', 'Made In USA', 'Over 15 Years in Business', 'Highest Quality', 'Fashion Forward', 'American Made & Owned']
        self.bodyStyleLibertyWear = {
                "SHORT SLEAVE TOPS": {"Name":"ADULT 18/1 - Heavier","Material":"100% Cotton", "Style" : "Short-Sleeve Tee", "eBayStyle" : "Graphic Tee", "eBaySizeType" : "Regular", "eBayCategory" : "15687", "SizePrice" : [("S",12.00),("M",12.00),("L",12.00),("XL",12.00),("XXL",13.50),("XXXL",14.50)]},
                "SF": {"Name":"ADULT 30/1 - Lighter","Material":"100% Cotton", "Style" : "Slim Fit Tee", "eBayStyle" : "Graphic Tee", "eBaySizeType" : "Slim Fit", "eBayCategory" : "15687", "SizePrice" : [("S",13.00),("M",13.00),("L",13.00),("XL",13.00),("XXL",14.50),("XXXL",15.50)]},
        }

        #use above dictionary to dumptruck insert records into sqlite3 database as json
        #indexes are used on every field
        if updateBodyStyleDict == True:
            self.dt.insert(self.bodyStyle,'bodyStyle', upsert=True)

        #read it all back
        bsd = self.dt.dump('bodyStyle')
        #grab just the latest row with latest data
        self.bodyStyle = dict(bsd[len(bsd)-1])

        #7049 Breast Cancer Shirt

        #bs = pd.read_sql('SELECT * from `bodyStyle` ORDER BY rowid DESC LIMIT 1;', self.conn)
        #bs = self.dt.execute('SELECT * from `bodyStyle` ORDER BY rowid DESC LIMIT 1;')

        self.xmlData = {}
        self.sizeLookup = {"Small":("S",1),"Medium":("M",2),"Large":("L",3),"XLarge":("XL",4),"2XLarge":("XXL",5),"3XLarge":("XXXL",6)}

        #self.pictureHost = r'http://24.8.122.237'
        self.pictureHost = r'http://s3.amazonaws.com/trevco/'
        #self.uploadXML = uploadXML0.replace(r'\xe2\x80\x8b','')

        self.uploadXML = '''
        <?xml version="1.0" encoding="utf-8"?>
        <UploadSiteHostedPicturesRequest xmlns="urn:ebay:apis:eBLBaseComponents">
        <WarningLevel>High</WarningLevel>
        <ExternalPictureURL>%(externalpictureurl)s</ExternalPictureURL>
        <PictureName>%(picturename)s</PictureName>
        <PictureSet>Supersize</PictureSet>
        <RequesterCredentials>
        <eBayAuthToken>AgAAAA**AQAAAA**aAAAAA**lou9Uw**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6wFk4GhCJmCpQ6dj6x9nY+seQ**GG8BAA**AAMAAA**cBaljKPzsKmG661he9KLvirBlCpzNwyJEluNXvMCyHWgQgRWe+/ZQ3fBshO9ZjllDLcjvu6niA8BKvIGuWfDPY+qwZH/eCjM8y+6i2Qda7ybLx+r2h+UGCAt1HM3I4UKipi5DsqMsm8VCNOsbfIFn1CeDo08bXiF29V1j+k6HpIf80xT51THCsLd3ZGwDfCsdPRUCKwyKA4SIJgMRHjHc0w5AstwDzTIS7Uwr42fh+lgIPfw6asklC4esGljDqBB1daejDQtUobyIx1q3nD1Obbht2fiQpsJkdCUs6l9ALnr9Y7Iaj38lFclMkvJk12XUXN8VyPnAdQUdpw9itBgEi94xCW4F8MPOfOS6OgePo5IGO3/J+oa2vYhKhH6rL3S2Avb98aOOr4keS5gccLa/OmVg2AfbjmgKyg9ERYcpmlqRtt4cYLxGJuM5q3GgHcs2oz1JUgCPNR6rfjM7Mt/Hkl7N2c56PhaxaRwIFQvb8V0MNv1eA5KvDfApZbNTgIiH6BK6eaAEaJCJzLmNO95CNofGCSQQDWOhdPTLB7of5IeRuqwVXOaBsQXnDF1zpIyIrJd3f0LKcfkj4+uyAUUUnt/cwPGcovfTaucv061D8fxqMaJbBdV1M4PgFI+yq+D5shqDo4M1aLWAFrZmACgGIxTQncvWXWP6CYDOjk119PXUP54SXTdyD1I3CnYCnkL5Xi4so8R4CDD49m0dhW+0qiwzCb6CX0I3C6N/3IDtpIF4ShQ2e96SQCdK+QTX3yy</eBayAuthToken>
        </RequesterCredentials>
        <WarningLevel>High</WarningLevel>
        </UploadSiteHostedPicturesRequest>​
        '''
        #self.dt.insert(self.uploadXML,'uploadXML', upsert=True)

        self.pictureDetails = '''<PictureURL>%(PictureURL2)s</PictureURL>
<PictureURL>%(PictureURL3)s</PictureURL>
<PictureURL>%(PictureURL4)s</PictureURL>
<PictureURL>%(PictureURL5)s</PictureURL>
<PictureURL>%(PictureURL6)s</PictureURL>
<PictureURL>%(PictureURL7)s</PictureURL>
<PictureURL>%(PictureURL8)s</PictureURL>
<PictureURL>%(PictureURL9)s</PictureURL>
<PictureURL>%(PictureURL10)s</PictureURL>
<PictureURL>%(PictureURL11)s</PictureURL>
<PictureURL>%(PictureURL12)s</PictureURL>'''

        self.xmlAddItemsRequest = '''<?xml version="1.0" encoding="utf-8"?>
<AddItemsRequest xmlns="urn:ebay:apis:eBLBaseComponents">
<ErrorLanguage>en_US</ErrorLanguage>
<WarningLevel>High</WarningLevel>
<AddItemRequestContainer>
<MessageID>1</MessageID>'''

        self.xmlString = '''<?xml version="1.0" encoding="utf-8"?>
<AddFixedPriceItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
<ErrorLanguage>en_US</ErrorLanguage>
<WarningLevel>High</WarningLevel>
<RequesterCredentials>
<eBayAuthToken>AgAAAA**AQAAAA**aAAAAA**lou9Uw**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6wFk4GhCJmCpQ6dj6x9nY+seQ**GG8BAA**AAMAAA**cBaljKPzsKmG661he9KLvirBlCpzNwyJEluNXvMCyHWgQgRWe+/ZQ3fBshO9ZjllDLcjvu6niA8BKvIGuWfDPY+qwZH/eCjM8y+6i2Qda7ybLx+r2h+UGCAt1HM3I4UKipi5DsqMsm8VCNOsbfIFn1CeDo08bXiF29V1j+k6HpIf80xT51THCsLd3ZGwDfCsdPRUCKwyKA4SIJgMRHjHc0w5AstwDzTIS7Uwr42fh+lgIPfw6asklC4esGljDqBB1daejDQtUobyIx1q3nD1Obbht2fiQpsJkdCUs6l9ALnr9Y7Iaj38lFclMkvJk12XUXN8VyPnAdQUdpw9itBgEi94xCW4F8MPOfOS6OgePo5IGO3/J+oa2vYhKhH6rL3S2Avb98aOOr4keS5gccLa/OmVg2AfbjmgKyg9ERYcpmlqRtt4cYLxGJuM5q3GgHcs2oz1JUgCPNR6rfjM7Mt/Hkl7N2c56PhaxaRwIFQvb8V0MNv1eA5KvDfApZbNTgIiH6BK6eaAEaJCJzLmNO95CNofGCSQQDWOhdPTLB7of5IeRuqwVXOaBsQXnDF1zpIyIrJd3f0LKcfkj4+uyAUUUnt/cwPGcovfTaucv061D8fxqMaJbBdV1M4PgFI+yq+D5shqDo4M1aLWAFrZmACgGIxTQncvWXWP6CYDOjk119PXUP54SXTdyD1I3CnYCnkL5Xi4so8R4CDD49m0dhW+0qiwzCb6CX0I3C6N/3IDtpIF4ShQ2e96SQCdK+QTX3yy</eBayAuthToken>
</RequesterCredentials>
</AddFixedPriceItemRequest>
'''

        self.xmlString2 = '''<item>
<ConditionID>1000</ConditionID>
<Country>US</Country>
<Currency>USD</Currency>
<Description>%(Description)s</Description>
<DispatchTimeMax>5</DispatchTimeMax>
<ListingDuration>GTC</ListingDuration>
<ListingType>FixedPriceItem</ListingType>
<PaymentMethods>PayPal</PaymentMethods>
<PayPalEmailAddress>payments@walkinauction.com</PayPalEmailAddress>
<PostalCode>95125</PostalCode>
<PrimaryCategory>
<CategoryID>%(CategoryID)s</CategoryID>
</PrimaryCategory>
<Title>%(Title)s</Title>
<PictureDetails>
<PictureURL>%(PictureURL1)s</PictureURL>
<PictureURL>%(PictureURL2)s</PictureURL>
<PictureURL>%(PictureURL3)s</PictureURL>
<PictureURL>%(PictureURL4)s</PictureURL>
<PictureURL>%(PictureURL5)s</PictureURL>
<PictureURL>%(PictureURL6)s</PictureURL>
<PictureURL>%(PictureURL7)s</PictureURL>
<PictureURL>%(PictureURL8)s</PictureURL>
<PictureURL>%(PictureURL9)s</PictureURL>
<PictureURL>%(PictureURL10)s</PictureURL>
<PictureURL>%(PictureURL11)s</PictureURL>
<PictureURL>%(PictureURL12)s</PictureURL>
</PictureDetails>
<ReturnPolicy>
<ReturnsAcceptedOption>ReturnsAccepted</ReturnsAcceptedOption>
<RefundOption>MoneyBack</RefundOption>
<ReturnsWithinOption>Days_14</ReturnsWithinOption>
<Description>You must contact us if you have any issues PRIOR to returning the item. 720-381-6789  Items must be received in the same condition sent and with any/all accessories originally included.  Restocking fee of 15 percent may apply.</Description>
<ShippingCostPaidByOption>Buyer</ShippingCostPaidByOption>
</ReturnPolicy>
<ShippingDetails>
<CalculatedShippingRate>
<OriginatingPostalCode>95125</OriginatingPostalCode>
<PackageDepth>6</PackageDepth>
<PackageLength>7</PackageLength>
<PackageWidth>7</PackageWidth>
<ShippingPackage>PackageThickEnvelope</ShippingPackage>
<WeightMajor>2</WeightMajor>
<WeightMinor>0</WeightMinor>
</CalculatedShippingRate>
<PaymentInstructions>Payment must be received within 7 business days of purchase.</PaymentInstructions>
<SalesTax>
<SalesTaxPercent>8.75</SalesTaxPercent>
<SalesTaxState>CA</SalesTaxState>
</SalesTax>
<ShippingServiceOptions>
<FreeShipping>true</FreeShipping>
<ShippingService>USPSPriority</ShippingService>
<ShippingServicePriority>1</ShippingServicePriority>
</ShippingServiceOptions>
<ShippingServiceOptions>
<ShippingService>UPSGround</ShippingService>
<ShippingServicePriority>2</ShippingServicePriority>
</ShippingServiceOptions>
<ShippingServiceOptions>
<ShippingService>UPSNextDay</ShippingService>
<ShippingServicePriority>3</ShippingServicePriority>
</ShippingServiceOptions>
<ShippingType>Calculated</ShippingType>
</ShippingDetails>
</item>'''

        self.shippingData = '''<ShippingDetails>
<CalculatedShippingRate>
<OriginatingPostalCode>95125</OriginatingPostalCode>
<PackageDepth>2</PackageDepth>
<PackageLength>7</PackageLength>
<PackageWidth>7</PackageWidth>
<ShippingPackage>PackageThickEnvelope</ShippingPackage>
<WeightMajor>1</WeightMajor>
<WeightMinor>0</WeightMinor>
</CalculatedShippingRate>
<PaymentInstructions>Immediate payment is expected.  Colorado residents will pay 4.6 percent sales tax.</PaymentInstructions>
<SalesTax>
<SalesTaxPercent>4.6</SalesTaxPercent>
<SalesTaxState>CO</SalesTaxState>
</SalesTax>
<ShippingServiceOptions>
<FreeShipping>true</FreeShipping>
<ShippingService>Standard Shipping (1 to 5 business days)</ShippingService>
<ShippingServicePriority>1</ShippingServicePriority>
</ShippingServiceOptions>
<ShippingType>Calculated</ShippingType>
</ShippingDetails>'''


    def oldFileOps(self):
        supplierIOFile = file2
        if file1:
            file_object_src = file1

            wb = xlrd.open_workbook(file_object_src)
            sheet = wb.sheet_by_name('Listings-Template')
            tempDF = pd.DataFrame()
            #column = sheet.col(1)
            # if values are extracted as numbers, we need to convert to int then str
            # otherwise just convert the value to str (also filtering headers)
            #numbers = map(lambda x: x.ctype==2 and str(int(x.value)) or str(x.value), column)
            for colnum in range(sheet.ncols):
                column = sheet.col(colnum)
                numbers = map(lambda x: x.ctype==2 and str(int(x.value)) or str(x.value), column)
                tempDF[colnum]=numbers
            self.srcFile = pd.io.excel.read_excel(file_object_src, sheetname='Listings-Template', index_col=None, na_values=['NA',''], header=2, skiprows=2)
            print(self.srcFile)

        if file2:
            #self.srcFile.
            file_object_dest = file2
            self.dest = pd.read_table(file_object_dest,dtype='str')

    def listMatching(self,Query):
        # Instantiate the Choreo
        listMatchingProductsChoreo = ListMatchingProducts(self.session)

        # Get an InputSet object for the Choreo
        listMatchingProductsInputs = listMatchingProductsChoreo.new_input_set()

        # Set the Choreo inputs
        listMatchingProductsInputs.set_AWSMarketplaceId(self.AWSMarketplaceId)
        listMatchingProductsInputs.set_Query(Query)
        listMatchingProductsInputs.set_AWSAccessKeyId(self.AWSAccessKeyId)
        listMatchingProductsInputs.set_Endpoint(self.Endpoint)
        listMatchingProductsInputs.set_AWSSecretKeyId(self.AWSSecretKeyId)
        listMatchingProductsInputs.set_AWSMerchantId(self.AWSMerchantId)

        # Execute the Choreo
        listMatchingProductsResults = listMatchingProductsChoreo.execute_with_results(listMatchingProductsInputs)

        # Print the Choreo outputs
        print("Response: " + listMatchingProductsResults.get_Response())

    def getMatching(self,Query):
        # Instantiate the Choreo
        getMatchingProductChoreo = GetMatchingProduct(self.session)

        # Get an InputSet object for the Choreo
        getMatchingProductInputs = getMatchingProductChoreo.new_input_set()

        # Set the Choreo inputs
        getMatchingProductInputs.set_AWSMarketplaceId(self.AWSMarketplaceId)
        getMatchingProductInputs.set_ASIN(Query)
        getMatchingProductInputs.set_AWSAccessKeyId(self.AWSAccessKeyId)
        getMatchingProductInputs.set_Endpoint(self.Endpoint)
        getMatchingProductInputs.set_AWSSecretKeyId(self.AWSSecretKeyId)
        getMatchingProductInputs.set_AWSMerchantId(self.AWSMerchantId)

        # Execute the Choreo
        getMatchingProductResults = getMatchingProductChoreo.execute_with_results(getMatchingProductInputs)
        #how to getNext???
        # Print the Choreo outputs
        self.queryResponse = getCompetitivePricingForASINResults.get_Response()
        #print("Response: " + getMatchingProductResults.get_Response())


    def getCompetitivePricingForAsin(self,Query):
        # Instantiate the Choreo
        getCompetitivePricingForASINChoreo = GetCompetitivePricingForASIN(self.session)

        # Get an InputSet object for the Choreo
        getCompetitivePricingForASINInputs = getCompetitivePricingForASINChoreo.new_input_set()

        # Set credential to use for execution
        #getCompetitivePricingForASINInputs.set_credential('amazonAWS')

        # Set the Choreo inputs
        getCompetitivePricingForASINInputs.set_AWSMarketplaceId(self.AWSMarketplaceId)
        getCompetitivePricingForASINInputs.set_ASIN(Query)
        getCompetitivePricingForASINInputs.set_AWSAccessKeyId(self.AWSAccessKeyId)
        getCompetitivePricingForASINInputs.set_Endpoint(self.Endpoint)
        getCompetitivePricingForASINInputs.set_AWSSecretKeyId(self.AWSSecretKeyId)
        getCompetitivePricingForASINInputs.set_AWSMerchantId(self.AWSMerchantId)

        # Execute the Choreo
        getCompetitivePricingForASINResults = getCompetitivePricingForASINChoreo.execute_with_results(getCompetitivePricingForASINInputs)

        # Print the Choreo outputs
        #self.queryResponse = getCompetitivePricingForASINResults.get_Response()
        return getCompetitivePricingForASINResults.get_Response()
        #print("Response: " + getCompetitivePricingForASINResults.get_Response())

    def procXML():
        # Instantiate the Choreo
        getValuesFromXMLChoreo = GetValuesFromXML(self.session)

        # Get an InputSet object for the Choreo
        getValuesFromXMLInputs = getValuesFromXMLChoreo.new_input_set()
        # Set the Choreo inputs
        getValuesFromXMLInputs.set_AWSMarketplaceId(self.AWSMarketplaceId)
        getValuesFromXMLInputs.set_ASIN(Query)
        getValuesFromXMLInputs.set_AWSAccessKeyId(self.AWSAccessKeyId)
        getValuesFromXMLInputs.set_Endpoint(self.Endpoint)
        getValuesFromXMLInputs.set_AWSSecretKeyId(self.AWSSecretKeyId)
        getValuesFromXMLInputs.set_AWSMerchantId(self.AWSMerchantId)

        # Execute the Choreo
        getValuesFromXMLResults = getValuesFromXMLChoreo.execute_with_results(getValuesFromXMLInputs)

        # Print the Choreo outputs
        print("Result: " + getValuesFromXMLResults.get_Result())

    def procXQuery(self, Query, xPathExpression, traverse='select'):
        # Instantiate the Choreo
        runXPathQueryChoreo = RunXPathQuery(self.session)

        # Get an InputSet object for the Choreo
        runXPathQueryInputs = runXPathQueryChoreo.new_input_set()
        # Set the Choreo inputs
        runXPathQueryInputs.set_XPath(xPathExpression)
        runXPathQueryInputs.set_XML(Query)
        runXPathQueryInputs.set_Mode(traverse)
        if traverse == 'recursive':
            runXPathQueryInputs.set_ResponseFormat("json")
        else:
            runXPathQueryInputs.set_ResponseFormat("csv")

        # Execute the Choreo
        #oc.runXPathQueryResults = runXPathQueryChoreo.execute_with_results(runXPathQueryInputs)
        getValuesFromXPathResults = runXPathQueryChoreo.execute_with_results(runXPathQueryInputs)
        return getValuesFromXPathResults.get_Result()
        # Print the Choreo outputs
        print("Result: " + runXPathQueryResults.get_Result())

    def trevcoShape(self):
        dest=None
        #LINE LIST 19JUN14.xlsx"
        #file_object_dest = r"C:\Users\bigal_000\Documents\trevco\LINE LIST 19JUN14 LIC.txt"
        # using the read_excel function
        #dest = ExcelFile.read_excel(file_object_dest, 'SUBLIMATED TEES', index_col=0, na_values=['NA'])
        #dest = pd.io.excel.read_excel(file_object_dest, sheetname='Temp', index_col=None, na_values=['NA',''])
        #'LICENSED DIGITAL'
        #dest = pd.io.excel.read_excel(file_object_dest,sheetname='LICENSED DIGITAL')
        destB = pd.DataFrame(oc.dest['DESCRIPTION'].str.replace("V-NECK","VNECK").str.split('-').tolist())
        del oc.dest['DESCRIPTION']

        #There are four rows that need fixing where column 4 has a size value (destB[4] > 0)
        #temp copy col0 to add back after combining col 1 and 2 then shifting all cols left 1
        #then add back col0
        #temporary store col0
        newCol0 = destB[destB[4] > 0][0]
        #make col1 and col2 as same column as temp newCol1
        newCol1 = destB[destB[4] > 0][1].map(str)+ " " + destB[destB[4] > 0][2]
        #shift to left all cols
        destC = destB[destB[4] > 0].shift(-1,axis=1)
        #reset shifted cols to temp cols
        destC[0] = newCol0
        destC[1] = newCol1
        #copy over entire grid shape and then set column names
        destB[destB[4] > 0] = destC
        del destB[4]
        #split title to list of line then description
        newCols = pd.DataFrame(destB[0].str.split(r'/',1).tolist())
        destD = pd.merge(destB,newCols, left_index=True, right_index=True)
        oc.workingGrid = destD
        oc.writeWorkingGrid()
        #set first set of column names then add the two new columns on the end
        oc.dest.columns = ['sku','product-id','price']
        destB.columns= ['title', 'type', 'color', 'size']
        oc.destC = pd.merge(oc.dest,destB,on=oc.dest.index, how='outer')
        oc.destC['line'] = destD['0_y']
        oc.destC['description'] = destD['1_y']
        oc.workingGrid = oc.destC

    def trevcoShape1(self):
        #strip nulls - 11 columns
        oc.grid0 = oc.workingGrid[pd.notnull(oc.workingGrid['BodyStyleDescription'])]
        #replace V-NECK - 1column
        oc.grid1 = pd.DataFrame(oc.grid0['BodyStyleDescription'].str.replace("V-NECK","VNECK"))
        #strip nulls - 11 columns
        oc.grid2 = pd.DataFrame(oc.grid0[pd.notnull(oc.grid0['DesignDescription'])])
        #only record with / - 11 columns
        oc.grid3 = pd.DataFrame(oc.grid2[oc.grid2['DesignDescription'].str.contains(r'/')])

        #oc.grid3 = oc.filterData('DesignDescription',r'/',oc.workingGrid)

        try:
            oc.grid5 = pd.DataFrame(oc.grid3['DesignDescription'].str.split(r'/',1).tolist(),columns=['brand','title'])
        except:
            print('Cannot parse design description field')
        #destD = pd.merge(oc.grid3, newCols, left_index=True, right_index=True)
        oc.grid6 = pd.merge(oc.grid3, oc.grid5,on=oc.grid3.index, how='outer')
        oc.workingGrid = oc.grid6[oc.grid6['SizeName'] != "One Size Fits All"]
        oc.workingGrid.title = oc.workingGrid.title.str.strip()
        oc.writeWorkingGrid(r'c:\test\workingGrid.csv')
        pass
        #.str.split('-').tolist())
        #destC = pd.DataFrame().from_csv(theFile)

    def supplierInternetRequest(self, httpRequest):
        #response = urllib2.urlopen(httpRequest)
        #fh = codecs.getreader("utf-8")(urllib.urlopen(httpRequest))
        self.httpRequest = httpRequest
        contentText = requests.get(httpRequest)
        doc = UnicodeDammit(contentText.text,is_html=True)
        parser = html.HTMLParser(encoding=doc.original_encoding)
        self.page = html.document_fromstring(contentText.text, parser=parser)


        #doc = UnicodeDammit(content, is_html=True)
        pass
        #self.htmlData = response.read()
        #print (self.htmlData)

    def supplierIO(self, supplierIOFile):
        #oc.workingGrid = pd.DataFrame().from_csv(supplierIOFile,index_col=0,dtype='str')
        oc.workingGrid = pd.read_table(supplierIOFile, dtype='str', index_col=0, sep=',', header=0, nrows=5000, error_bad_lines=False, warn_bad_lines=True)
        #oc.workingGrid = pd.read_table(supplierIOFile, dtype='str', index_col=0, sep=',', header=0, error_bad_lines=False, warn_bad_lines=True)
        #remove_re = re.compile(u'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F-\xc3\x89]')
        #CAF\xc3\x89 DIEM
        #oc.text = remove_re.sub('', oc.workingGrid.)
        #oc.workingGrid.replace(remove_re,'')
        pass

    def ebayIO(self):
        pass

    def amazonIO(self, amazonFile):
        self.ffc = amazonFile
        pass

    def htmlParser(self):
        #soup = BeautifulSoup(oc.htmlData)
        pageInfo ={}
        pageKey = oc.httpRequest.split("/",3)[3].split(".")[0].split("-")[0]
        pageInfo.setdefault(pageKey,{})
        #myparser = etree.HTMLParser(encoding="utf-8")
        #myparser = html.html_parser(encoding=oc.page.original_encoding)
        #root = html.document_fromstring(content, parser=parser)

        tree = oc.page
        #tree = etree.HTML(oc.page, parser=myparser)
        #tree = html.fromstring(oc.page.content, parser=myparser)

        pageInfo[pageKey].setdefault('page', oc.httpRequest)
        pageInfo[pageKey].setdefault('breadcrumb', tree.xpath('//div[@class="breadcrumb"]/span/a/text()'))

        pageInfo[pageKey].setdefault('description',tree.xpath('//div[@class="Description"]/span/text()')[0])
        pageInfo[pageKey].setdefault('bullets', tree.xpath('//div[@class="Description"]/span/ul/li/text()'))
        pageInfo[pageKey].setdefault('price', tree.xpath('//span[@class="SalePrice"]/text()'))

        #use above dictionary to dumptruck insert records into sqlite3 database as json
        #indexes are used on every field
        oc.dt.insert(pageInfo,'pageInfo', upsert=True)
        #read it all back
        bsd = self.dt.dump('pageInfo')
        #grab just the latest row with latest data
        self.parsedHtml = dict(bsd[len(bsd)-1])
        pass

    def getLatestDownloadFile(self):
        downloadDir=r'C:\Users\bigal_000\Downloads' # path to your log directory
        #lastFile = sorted([ f for f in os.listdir(downloadDir)])
        self.workingFile = max(glob.iglob(downloadDir + '\*.*'), key=os.path.getctime)
        #self.workingFile=(lastFile[-1])
        oc.workingGrid = pd.read_table(self.workingFile, dtype='str', index_col=0, sep=',', header=0, nrows=5000, error_bad_lines=False, warn_bad_lines=True)
        pass

    def amazonHelper(self, headerText, skuTypeMatch, valueMatch):
        pf = pd.read_excel(oc.ffc, sheetname='Valid Values', header=1)
        headerTextList = headerText.split("_")
        validValues = pf[headerText].loc[(pf[headerText].notnull())]
        print(validValues)
        styleCount = 0
        for s,t in validValues.iteritems():
            for j in t.split():
                    for dictCode,dictData in oc.bodyStyle.iteritems():
                        if any(j.lower() in jj for jj in headerTextList):
                            continue

                        for v, m in valueMatch.iteritems():
                            if j == v:
                                j = m

                        #if j == "Sleeveless" or j == "Tanks":
                        #    j = "Tank"
                        #elif j == "Fit":
                        #    j = "Short"

                        print "Looking for: " + j + " in " + dictData[skuTypeMatch]
                        if dictData[skuTypeMatch].lower().find(j.lower()) > -1:
                            oc.bodyStyle[dictCode].setdefault(u'storefront',{}).setdefault(u'amazon',{})[headerText] = t
                            print("*****Found****")
                            styleCount += 1
                        elif dictData[skuTypeMatch].lower().find(j.lower()) > -1:
                            oc.bodyStyle[dictCode].setdefault(u'storefront',{}).setdefault(u'amazon',{})[headerText] = t
                            print("*****Found****")
                            styleCount += 1

        for sn in oc.bodyStyle.iteritems():
            print("Verifying " + str(sn[0]))
            try:
                if oc.bodyStyle[sn[0]][u'storefront'][u'amazon'][headerText]:
                    print("    Found style " + oc.bodyStyle[sn[0]][u'storefront'][u'amazon'][headerText])
            except:
                print ("    *** Error *** - need stylename for " + sn[0])

        oc.dt.insert(oc.bodyStyle,'pageInfo', upsert=True)
        oc.dt.dump('pageInfo')

        fp = open(r'c:\test\jsonfile.txt','w')
        json.dump(oc.bodyStyle,fp, indent=2, sort_keys=True)
        fp.close()


    def amazonBatch(self):
        pf = pd.read_table(oc.ffc, header=2, dtype=str, sep=",")
        #wb = xlrd.open_workbook(oc.ffc)

        # if values are extracted as numbers, we need to convert to int then str
        # otherwise just convert the value to str (also filtering headers)
        #numbers = map(lambda x: x.ctype==2 and str(int(x.value)) or str(x.value), column)

        #validValues = pf.loc[(pf.notnull())]
        self.workingGrid = pf.dropna(axis=1,how='all')
        res = self.workingGrid.loc[self.workingGrid['parent_child']=='parent']
        res1 = res.dropna(axis=1,how='all')
        parentItemDict = {}
        parentItemDict['template']={}
        for j in res1.columns:
            parentItemDict['template'][j]=''

        oc.dt.insert(parentItemDict,'parentItemDict',upsert=True)
        pass

    def csv_from_excel():
        wb = xlrd.open_workbook('your_workbook.xls')
        sh = wb.sheet_by_name('Sheet1')
        your_csv_file = open('your_csv_file.csv', 'wb')
        wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)

        for rownum in xrange(sh.nrows):
            wr.writerow(sh.row_values(rownum))

        your_csv_file.close()

    def ebayPictures(self):
        pass

    def ebayBatch(self, brandList=None):
        #Once Trevco data is re-shaped - new column with \ split on brand and design
        #then group by the first column e.g. Abbott & Costello brand.unique()
        if brandList is None:
            uniqueBrand = oc.workingGrid['brand'].unique()
        else:
            uniqueBrand = brandList

        #set category and valid sizes lists
        catList = []
        validSizesList = []
        validSizesList = set(oc.sizeLookup.keys())

        #a unique brand is like ARCHIE COMICS
        for item in uniqueBrand:
            self.logger.info('item:' + item)
            oc.xmlData = {}
            #Include top of XML message here (Everything from Item - ItemSpecifics
            #df.loc[df['column_name'] == some_value]
            grid0 = pd.DataFrame()
            #comment for color as a variation - still need logic for this
            grid0 = oc.workingGrid.loc[(oc.workingGrid['brand']==item) & (oc.workingGrid['BodyStyleDescription'].str.contains("ADULT") & oc.workingGrid['SizeName'].isin(validSizesList) & oc.workingGrid['ShirtColor'].notnull())]
            #grid0 = oc.workingGrid.loc[(oc.workingGrid['brand']==item) & (oc.workingGrid['BodyStyleDescription'].str.contains("ADULT") & oc.workingGrid['SizeName'].isin(validSizesList))]
            uDesignNames = grid0.title.unique()

            #Should only process 12 titles at a time because that's how many pictures are allowed for each variation
            #code below makes a list of lists with 12 items that is used to filter the grid in an outer loop
            #ebay has a max of 250 variations so need to calculate that number somewhere (first place we know we can)
            innerList = []
            outerList = []
            designCount = len(uDesignNames)
            L = range(designCount)
            if designCount > 12:
                self.logger.info("Design Count for ")
                for x in L[::12]:
                    for dName in uDesignNames[x-12:x]:
                        innerList.append(dName)
                    outerList.append(innerList)
                    innerList = []
                if len(outerList) > 0:
                    outerList.pop(0)
            else:
                outerList = uDesignNames

            #outerList now contains either 1 list of 12 or less designs or many lists
            #of 12 or less designs
            for designName in outerList:
                self.logger.info('designName:'+ str(designName))
                wgrid0 = grid0.loc[grid0.title.isin(uDesignNames)]
                filestringname = item + '-' + designName[0] + '-' + designName[-1]
                output = open('c:\\test\\trevco_mens_listings\\' + ''.join(e for e in filestringname if e.isalnum()) + '.xml','w')

                bodyCodes = pd.DataFrame()
                bodyCodes = wgrid0['BodyCode'].unique()
                uniqueSizeNames = pd.DataFrame()
                uniqueSizeNames = wgrid0['SizeName'].unique()
                uniqueImageNames = pd.DataFrame()
                uniqueImageNames = wgrid0['Image'].unique()

                #build list of base designs for use in picture1-12 in listing item level
                res1 = []
                resError = {}
                baseDesigns = []

                for bd in uniqueImageNames:
                    baseDesigns.append(bd.split('-')[0] + '.jpg')
                ubaseDesigns = set(baseDesigns)
                uniqueNames = []

                for ii in range(2):
                    if ii == 0:
                        uniqueNames = uniqueImageNames
                    if ii == 1:
                        uniqueNames = ubaseDesigns
                    #loop through unique images and upload pictures to ebay that have not been uploaded already
                    #could put code here to check date and make sure n(30?) days elapsed since picture will be removed by ebay
                    for pic in uniqueNames:
                        oc.xmlData['externalpictureurl'] = self.pictureHost + pic
                        oc.xmlData['picturename'] = pic[:-4]

                        #loop through uploaded picture data to avoid re-posting picture to ebay
                        try:
                            res2 = oc.dt.dump('pictures')
                        except:
                            self.logger.info("Error getting sqlite3 table pictures")
                            continue

                        if str(res2).find(oc.xmlData['externalpictureurl']):
                            continue
                        else:
##                        for r in res2:
##                            try:
##                                self.logger.info("Looking for " + r['SiteHostedPictureDetails']['PictureName'])
##                                if r['SiteHostedPictureDetails']['PictureName'] == oc.xmlData['picturename']:
##                                    continue
##                                else:
                            pictureData = {
                                "WarningLevel": "High",
                                "ExternalPictureURL": oc.xmlData['externalpictureurl'],
                                "PictureName": oc.xmlData['picturename'],
                                "PictureSet": "Supersize"
                            }
                            try:
                                res = json.loads(trading.uploadPicture(oc.opts, pictureData))
                                oc.dt.insert(res,'pictures', upsert=True)
                                #res1.append(res)
                            except:
                                self.logger.info("Error " + str(pictureData))
                                print("Error " + str(pictureData))
                                resError['Error'] = str(pictureData)
                                oc.dt.insert(resError,'err')
                                #res1.append(resError)
                    pass

##                    except:
##                        self.logger.info("Problem processing uploadSiteHostedPictures")

                    #fp = open(r'c:\test\pictures.txt','a')
                    #json.dump(res1,fp, indent=2, sort_keys=True)
                    #fp.close()
                    #oc.inplace_change(r'c:\test\pictures.txt',r'][',r',')

                            #encode image files
                            #for uFile in uniqueImageNames:
                            #    imageFileName = 'E:\\trevco\\ALL_LicensedImages\\' + uFile
                            #    #encode to string or delete line with image that cannot be found
                            #    try:
                            #        with open(imageFileName,'rb') as img:
                            #            encoded_str = base64.b64encode(img.read())
                            ###            pass
                            #    except:
                            #        wgrid0 = wgrid0[wgrid0.Image != uFile]

                            #uniqueSizeNames = uniqueSizeNames[numpy.logical_not(numpy.isnan(uniqueSizeNames))]
                            #uniqueSizeNames.dropna()
                eBaySizesList = []
                for l in uniqueSizeNames:
                    if not pd.isnull(l):
                        eBaySizesList.append(oc.sizeLookup[l])

                #make sure all sizes for brand are sorted for item specific xml building
                eBaySizesList.sort(key=lambda x: x[1])
                eBaySortedBrandSizeList = [i[0] for i in eBaySizesList]

                #Then group by bc = BodyCode.unique()
                #loop through bc AND MAP to bodyStyle dict to get a list of all categories
                catList = []
                catStyleList = []
                for bc in bodyCodes:
                    try:
                        catList.append((oc.bodyStyle[bc]['eBayCategory']))
                        catStyleList.append((bc,oc.bodyStyle[bc]['eBayCategory'],oc.bodyStyle[bc]['eBaySizeType'],oc.bodyStyle[bc]['Style']))
                    except:
                        pass

                uniqueCategories = set(catList)
                #Now should have all info to process and write xml files
                #Once all xml files are written, we should loop through them and validate them
                #then send a sample through the sandbox.
                #Need to manually add required item specifics to oc.bodyStyle dict to make
                #the builder more robust
                #Still need a function to write picture file and save URL to build these listings

                #FOR EACH UNIQUE CATEGORY FOR EACH BRAND THEN START NEW XML FILE/NEW LISTING that will include
                #all of the body styles and variations for that category/brand

                for cat in uniqueCategories:
                    self.logger.info('cat:'+cat)
                    #get unique list of bodyTypes from product grid that matches current category
                    #use isin operator on bodyTypes to filter grid
                    styleList = []
                    typeList = []
                    stylenameList = []
                    for s,c,t,y in catStyleList:
                        if c == cat:
                            styleList.append(s)
                            typeList.append(t)
                            stylenameList.append(y)

                    uniqueStyles = set(styleList)
                    uniqueTypes = set(typeList)
                    uniqueStylenames = set(stylenameList)
                    uniqueColors = wgrid0['ShirtColor'].unique()

                    #filter the grid to only include styles in category
                    grid1 = wgrid0.loc[wgrid0['BodyCode'].isin(styleList)]
                    testGrid = pd.DataFrame()
                    testGrid = grid1
                    if testGrid.empty:
                        continue
                    uTitles = grid1['title'].str.strip().unique()


                    #todo get first 3 of item and make a dict for each 3 letter code mapped to string
                    #that actually gives brand like DCO : DC Comics
                    #oc.workingGrid['key_0'].str[:3].unique()
                    #xmlString = etree.fromstring(xmlString)

                    #descriptionText = r'<![CDATA[New Ralph Lauren Polo womens tops shirts! Black, Pink, Yellow, Blue. NWT]]>'
                    oc.xmlData['Description'] = r'<![CDATA[New ' + escape(grid1['brand'][grid1.index[0]]) + ' Certified Tees with Many Unique Design and Material Combinations]]>'
                    #oc.xmlData['Description'] = "New " + grid1['brand'][grid1.index[0]] + " Certified Tees with Many Unique Design and Material Combinations"
                    oc.xmlData['CategoryID'] = cat
                    oc.xmlData['Title'] = escape("New " + grid1['brand'][grid1.index[0]] + " Certified Tees - Many Unique Design Combinations")
                    #maybe put gallery grid maker here

                    #need to convert this code into montage maker and use 1-12 in item pics
                    #as size charts - for size charts we need size chart filename in bodyStyles dict
                    ubaseDesignsList = []
                    for row in ubaseDesigns:
                        ocpic11 = oc.picLookup(row)
                        if ocpic11:
                            ubaseDesignsList.append((row,ocpic11))

                    for i, baseDesignFile in enumerate(ubaseDesigns, start=1):
                        if i > len(ubaseDesignsList):
                            break
                        #oc.xmlData['PictureURL' + i] = oc.pictureHost + grid1['Image'][grid1.index[0]]
                        oc.xmlData['PictureURL' + str(i)] = ubaseDesignsList[i-1][1]

                    #replace data in xml
                    newXML = oc.xmlString2%oc.xmlData
                    newXML1 = newXML.replace("\n","")

                    root = etree.fromstring(oc.xmlString)

                    itemnode = etree.fromstring(newXML1)
                    #tree = etree.ElementTree(root)
                    #root = etree.Element("AddFixedPriceItemRequest")
                    #itemnode = etree.Element("item")
                    root.insert(2,itemnode)

                    #XML fro ItemSpecifics on
                    itemspecifics1 = etree.SubElement(itemnode,"ItemSpecifics")
                    namevaluelist1 = etree.SubElement(itemspecifics1,"NameValueList")
                    thename1 = etree.SubElement(namevaluelist1,"Name")
                    thename1.text = "Brand"
                    thename2 = etree.SubElement(namevaluelist1,"Value")
                    thename2.text = grid1['brand'][grid1.index[0]]
                    thename22 = etree.SubElement(namevaluelist1,"Name")
                    thename22.text = "Style"
                    thename33 = etree.SubElement(namevaluelist1,"Value")
                    thename33.text = "Graphic Tee"

                    #itemspecifics code here

                    #These are going to be at the variation level
                    #as long as you use the exact same item specific name then you
                    #can put them at that level and they count toward required item specifics
                    #make list of all size types and set variable to check if manySizeTypes
                    #Then add them at the variation level, else add them here

                    if len(uniqueTypes) < 2:
                        namevaluelist1 = etree.SubElement(itemspecifics1,"NameValueList")
                        thename2 = etree.SubElement(namevaluelist1,"Name")
                        thename2.text = "Size Type"
                        thename3 = etree.SubElement(namevaluelist1,"Value")
                        thename3.text = "Regular"

                        #print(etree.tostring(root, pretty_print=True))

                        namevaluelist2 = etree.SubElement(itemspecifics1,"NameValueList")
                        thename4 = etree.SubElement(namevaluelist2,"Name")
                        thename4.text = "Garment Style"
                        thename5 = etree.SubElement(namevaluelist2,"Value")
                        thename5.text = oc.bodyStyle[grid1['BodyCode'][grid1.index[0]]]['eBayStyle']

                    variationCounter = 0
                    #NOW FINALLY TIME TO MAKE VARIATIONS!!!
                    for index, row in grid1.iterrows():
                        if variationCounter == 0:
                            variations = etree.SubElement(itemnode,"Variations")
                            variationspecificset = etree.SubElement(variations,"VariationSpecificsSet")
                            namevaluelist3 = etree.SubElement(variationspecificset,"NameValueList")

                            #Size and Design are displayed for all variations
                            #Size Type and Style are only displayed here for listings with many types
                            #unique designs
                            uTitle = grid1['title'].str.strip().unique()
                            thename6 = etree.SubElement(namevaluelist3,"Name")
                            thename6.text = "Design"
                            #For each design, concat design + style as first drop down list contents
                            try:
                                for var1 in uTitle:
                                    #new
                                    for us in uniqueStyles:
                                        thename7 = etree.SubElement(namevaluelist3,"Value")
                                        thename7.text = var1.strip()+us

                            except:
                                pass

                            #if oc.bodyStyle[row['BodyCode']['eBaySizeType']:
                            #if manySizeTypes == True:
                            needBodyAndSizeVariationSpecifics = False
                            if len(uniqueTypes) > 1:
                                needBodyAndSizeVariationSpecifics = True
                                #unique size types - Regular or Slim Fit
                                uTypeList = set(typeList)
                                #u = grid1[12].unique()
                                namevaluelist4 = etree.SubElement(variationspecificset,"NameValueList")
                                thename8 = etree.SubElement(namevaluelist4,"Name")
                                thename8.text = r"Size Type"

                                for uTypeListItem in uTypeList:
                                    thename9 = etree.SubElement(namevaluelist4,"Value")
                                    thename9.text = uTypeListItem

                                #only 1 garment so only 1 body style too
                                #unique body styles
                                uStyleList = set(styleList)
                                namevaluelist5 = etree.SubElement(variationspecificset,"NameValueList")
                                thename10 = etree.SubElement(namevaluelist5,"Name")
                                thename10.text = "Garment Style"

                                for uStyleListItem in uStyleList:
                                    thename11 = etree.SubElement(namevaluelist5,"Value")
                                    thename11.text = oc.bodyStyle[uStyleListItem]['Material'] + oc.bodyStyle[uStyleListItem]['Name'].replace('ADULT','')

                            if len(uniqueColors) > 1:
                                #make variation list for unique colors
                                colorvaluelist = etree.SubElement(variationspecificset,"NameValueList")
                                colorname = etree.SubElement(colorvaluelist,"Name")
                                colorname.text = "Color"

                                for colorItem in uniqueColors:
                                    colorvariation = etree.SubElement(colorvaluelist,"Value")
                                    colorvariation.text = colorItem

                            #unique sizes
                            ueBaySortedBrandSizeList = eBaySortedBrandSizeList
                            namevaluelist6 = etree.SubElement(variationspecificset,"NameValueList")
                            thename12 = etree.SubElement(namevaluelist6,"Name")
                            thename12.text = r"Size (Men's)"

                            for ueBaySortedBrandSizeListItem in ueBaySortedBrandSizeList:
                                thename13 = etree.SubElement(namevaluelist6,"Value")
                                thename13.text = ueBaySortedBrandSizeListItem
                        else:
                            #####################################################################################
                            # Now add Variations --- 1 for each combination from variation block above
                            #####################################################################################
                            variation = etree.SubElement(variations,"Variation")

                            #variationspecificset = etree.SubElement(variations,"VariationSpecificsSet")

                            thenameA = etree.SubElement(variation,"SKU")
                            thenameA.text = "WIA_" + row['key_0']
                            thenameB = etree.SubElement(variation,"StartPrice")
                            theSizeLookup = oc.sizeLookup[row['SizeName']][0]

                            #print theSizeLookup, row['key_0']
                            #try:
                            thenameB.text = str((dict(self.bodyStyle[row['BodyCode']]['SizePrice'])[theSizeLookup])*2)
                            #except:
                            #    pass
                            thenameC = etree.SubElement(variation,"Quantity")
                            thenameC.text = "3"

                            #####################################################################################
                            # Now add VariationSpecifics --- 1 for each combination from variations block above
                            #####################################################################################
                            variationspecifics = etree.SubElement(variation,"VariationSpecifics")
                            namevaluelistA = etree.SubElement(variationspecifics,"NameValueList")
                            #variationspecificset = etree.SubElement(variationspecificset,"NameValueList")
                            thenameD = etree.SubElement(namevaluelistA,"Name")
                            thenameD.text = r"Design"
                            thenameE = etree.SubElement(namevaluelistA,"Value")
                            thenameE.text = row['title'].strip()
                            shirtStyleList = []

                            namevaluelistB = etree.SubElement(variationspecifics,"NameValueList")
                            #variationspecificset = etree.SubElement(variationspecificset,"NameValueList")
                            thenameF = etree.SubElement(namevaluelistB,"Name")
                            thenameF.text = r"Size (Men's)"
                            thenameG = etree.SubElement(namevaluelistB,"Value")
                            thenameG.text = theSizeLookup

                            if needBodyAndSizeVariationSpecifics == True:
                                sbc = row['BodyCode']
                                shirtStyleList.append((sbc,oc.bodyStyle[sbc]['eBayCategory'],oc.bodyStyle[sbc]['eBaySizeType'],oc.bodyStyle[sbc]['Style'], oc.bodyStyle[sbc]['Material'],oc.bodyStyle[sbc]['Name'].replace('ADULT','')))
                                #unique size types - Regular or Slim Fit
                                namevaluelist5 = etree.SubElement(variationspecifics,"NameValueList")
                                thename14 = etree.SubElement(namevaluelist5,"Name")
                                thename14.text = r"Size Type"

                                thename15 = etree.SubElement(namevaluelist5,"Value")
                                thename15.text = shirtStyleList[0][2]

                                #only 1 garment so only 1 body style too
                                #unique body styles
                                namevaluelist6 = etree.SubElement(variationspecifics,"NameValueList")
                                thename16 = etree.SubElement(namevaluelist6,"Name")
                                thename16.text = "Garment Style"

                                thename17 = etree.SubElement(namevaluelist6,"Value")
                                thename17.text = shirtStyleList[0][4] + shirtStyleList[0][5]

                            if len(uniqueColors) > 1:
                                #make variation specifics for unique colors
                                colorvariationlist = etree.SubElement(variationspecifics,"NameValueList")
                                colorvariationspecificsname = etree.SubElement(colorvariationlist,"Name")
                                colorvariationspecificsname.text = "Color"

                                colorvariationspecificsvalue = etree.SubElement(colorvariationlist,"Value")
                                colorvariationspecificsvalue.text = row['ShirtColor'].strip()

                        variationCounter += 1

                    pictures = etree.SubElement(variations,"Pictures")

                    #Design Variation Pictures (1 picture for each design)
                    designvariationspecificname = etree.SubElement(pictures, "VariationSpecificName")
                    designvariationspecificname.text = "Design"
                    designvariationspecificpictureset = etree.SubElement(pictures, "VariationSpecificPictureSet")

                    for t in uTitle:
                        grid2 = grid1.loc[grid1['title'] == t]
                        uImage = pd.DataFrame(grid2['Image'].unique())

                        designvariationspecificvalue = etree.SubElement(designvariationspecificpictureset,"VariationSpecificValue")
                        designvariationspecificvalue.text = t

                        for index, row in uImage.iterrows():
                            ocpic00 = oc.picLookup(row[0])
                            if ocpic00:
                                pictureurl = etree.SubElement(designvariationspecificpictureset,"PictureURL")
                                pictureurl.text = ocpic00

                    if needBodyAndSizeVariationSpecifics == True:
                        #BodyType variation Pictures (for each bodytype print all designs)
                        variationspecificname = etree.SubElement(pictures, "VariationSpecificName")
                        variationspecificname.text = "Garment Style"
                        variationspecificpictureset = etree.SubElement(pictures, "VariationSpecificPictureSet")
                        for y in uStyleList:
                            #thename11 = etree.SubElement(namevaluelist5,"Value")
                            #thename11.text = oc.bodyStyle[uStyleListItem]['Material'] + oc.bodyStyle[uStyleListItem]['Name'].replace('ADULT','')

                            grid3 = grid1.loc[grid1['BodyCode'] == y]
                            uBodyCodePicture = pd.DataFrame(grid3['Image'].unique())

                            variationspecificvalue = etree.SubElement(variationspecificpictureset,"VariationSpecificValue")
                            variationspecificvalue.text = oc.bodyStyle[y]['Material'] + oc.bodyStyle[y]['Name'].replace('ADULT','')

                            for index, row in uBodyCodePicture.iterrows():
                                ocpic0 = oc.picLookup(row[0])
                                if ocpic0:
                                    pictureurl = etree.SubElement(variationspecificpictureset,"PictureURL")
                                    pictureurl.text = ocpic0

                    if len(uniqueColors) > 1:
                        #pictures for each color
                        #Design Variation Pictures (1 picture for each design)
                        colorvariationspecificname = etree.SubElement(pictures, "VariationSpecificName")
                        colorvariationspecificname.text = "Color"
                        colorvariationspecificpictureset = etree.SubElement(pictures, "VariationSpecificPictureSet")

                        for c in uniqueColors:
                            colorGrid = grid1.loc[grid1['ShirtColor'] == c]
                            uColorImage = pd.DataFrame(colorGrid['Image'].unique())

                            colorvariationspecificvalue = etree.SubElement(colorvariationspecificpictureset,"VariationSpecificValue")
                            colorvariationspecificvalue.text = c

                            for index, row in uColorImage.iterrows():
                                ocpic1 = oc.picLookup(row[0])
                                if ocpic1:
                                    pictureurl = etree.SubElement(colorvariationspecificpictureset,"PictureURL")
                                    pictureurl.text = ocpic1


                    et = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='utf-8')
                    #output = open(r'c:\test\ebay_listings.xml','w')
                    output.write(et)
                    output.close()
                    pass


    def picLookup(self, thePic):
        res2 = oc.dt.dump('pictures')
        foundPicName = False
        for r in res2:
            try:
                self.logger.info("Looking for picture match " + thePic[:-4])
                if r['SiteHostedPictureDetails']['PictureName'] == thePic[:-4]:
                    return r['SiteHostedPictureDetails']['FullURL']
            except:
                self.logger.info("SiteHostedPictureDetails Error")
                #print("SiteHostedPictureDetails Error")

    def wikiAttribution(self, searchTerm):
            a = wikipedia.search(searchTerm)
            b = wikipedia.page(a[0])
            theUrl = b.url
            theTitle = b.title
            return theTitle + " licensed under CC-BY-SA"

    def writeTheFile():
        output = StringIO.StringIO()
        output.write('First line.\n')
        print >>output, 'Second line.'

        # Retrieve file contents -- this will be
        # 'First line.\nSecond line.\n'
        contents = output.getvalue()

        # Close object and discard memory buffer --
        # .getvalue() will now raise an exception.
        output.close()

    def amazonPricing(self):
        asinList = list(oc.asinVals.splitlines())
        asinQuery = ''
        asinAndPriceList = []

        for i in range(6):
            j=0
            for asin in asinList:
                j+=1
                if asin == r"'B00IABP9ZC'":
                    print "********************************************" + asin
                if(j%20 == 0) and (j > 0):
                    asinQuery += asin
                    asinListResults = []
                    priceListResults = ''

                    theQuery = oc.getCompetitivePricingForAsin(asinQuery)
                    #theQuery = oc.queryResponse
                    xPathExpression = "/GetCompetitivePricingForASINResponse/GetCompetitivePricingForASINResult/@ASIN"
                    asinListResults = oc.procXQuery(theQuery, xPathExpression, 'recursive')
                    xPathExpression = "/GetCompetitivePricingForASINResponse/GetCompetitivePricingForASINResult/Product/CompetitivePricing/CompetitivePrices/CompetitivePrice/Price/ListingPrice"
                    priceListResults = oc.procXQuery(theQuery, xPathExpression, 'recursive')
                    js = json.loads(priceListResults)
                    #print(asinListResults, js[0])
                    for x, asinVal in enumerate(json.loads(asinListResults)):
                        #print(asinVal, js[x]['Amount'])
                        asinAndPriceList.append((asinVal, js[x]['Amount']))
                        asinList.pop(0)
                    asinQuery = ''
                    j=0
                    pass
                else:
                    asinQuery += asin + ','

        with open(r'c:\test\asin_price.csv', 'wb') as f:
            writer = csv.writer(f)
            writer.writerows(asinAndPriceList)

    def filterData(self, colId, rowFilter, fGrid):
        #takes int or string for colId to filter grid on one column
        try:
            fGrid = oc.workingGrid
        except:
            return None
        try:
            print fGrid[fGrid[colId].str.contains(rowFilter)]
            return fGrid[fGrid[colId].str.contains(rowFilter)]
        except:
            print fGrid[fGrid[str(colId)].str.contains(rowFilter)]
            return fGrid[fGrid[str(colId)].str.contains(rowFilter)]
        else:
            return None

    def joinOp(self):
        #This merge is for joining the left/first part of the table with the right/last part
        oc.filteredDest = pd.merge(theFilter,oc.srcFile,left_on=theFilter['product-id'], right_on=oc.srcFile['product-id'], how='inner')
        print(oc.destC)

    def writeWorkingGrid(self, thePath=r'c:\test\test.csv'):
        #with open(r'c:\test\workingGrid.csv', 'wb') as f:
        #    writer = csv.writer(f)
        #    writer.writerows(oc.workingGrid)
        oc.workingGrid.to_csv(thePath,sep="\t", index=False)

def proc_eBay():
    oc.supplierIO(r"C:\Users\bigal_000\Documents\trevco\TrevcoItemsList.csv")
    oc.trevcoShape1()
    brandList = ['ABBOTT & COSTELLO']
    #brandList = None
    oc.ebayBatch(brandList)

def proc_amazon_helper():
    #this is extreme data processing - lookup amazon spreadsheet values
    #for valid values and build out existing dictionary on the fly for supplier data
    #oc.supplierIO(r"C:\Users\bigal_000\Documents\trevco\TrevcoItemsList.csv")
    #oc.trevcoShape1()
    oc.amazonIO(r"C:\Users\bigal_000\Downloads\Flat.File.Clothing.xls")
    valueMatch = {'Sleeveless':'Tank','Tanks':'Tank', 'Fit':'Short'}
    skuTypeMatch = 'Style'
    oc.amazonHelper(u'sleeve_type', skuTypeMatch, valueMatch)

    valueMatch = {'short':'DONOTMATCH'}
    skuTypeMatch = 'Style'
    oc.amazonHelper(u'special_size_type', skuTypeMatch, valueMatch)

def proc_amazon_flat_file_clothing_xl():
    #oc.amazonIO(r"C:\Users\bigal_000\Downloads\Flat.File.Clothing.xls")
    oc.amazonIO(r"C:\Users\bigal_000\Documents\WIAStires Flat.File.Clothing.xls")
    oc.amazonBatch()
    pass

def proc_amazon_flat_file_clothing_csv():
    #oc.amazonIO(r"C:\Users\bigal_000\Downloads\Flat.File.Clothing.xls")
    oc.amazonIO(r'C:\Users\bigal_000\Documents\WIAStires Flat.File.Clothing.csv')
    oc.amazonBatch()
    pass

if __name__ == "__main__":
    #createAmazonSession = True
    #updateBodyStyleDict = True

    logger = logging.getLogger(__name__)
    logger.info("Begin Program")
    oc = OC()
    #proc_amazon_helper()
    #proc_amazon_flat_file_clothing_xl()
    proc_amazon_flat_file_clothing_csv()
    #get file from ecomdash for instance
    #oc.getLatestDownloadFile()


    #parse internet data from supplier
    rockList = [r'http://www.rockmount.com/7787-blk-sml-floral-embroidered-shirt.aspx',r'http://www.rockmount.com/7718-ivory-sml-floral-embroidery-cotton-gab-western-shirt.aspx',r'http://www.rockmount.com/6854-tan-blk-sml-steam-punk-western-shirt.aspx']
    for i in range(1):
        res = oc.supplierInternetRequest(rockList[i])
        res = oc.htmlParser()

    #oc.listMatching("887806214400")

    #proc_eBay()


    #proc_amazon_helper()


    #oc = OC(None,r"C:\Users\bigal_000\Documents\trevco\LINE LIST 19JUN14 LIC.txt")			# instantiate the application

    #oc.output.close()
    #theFilter = oc.filterData('title','BATMAN ARKHAM ORIGINS')
    #oc.writeWorkingGrid(r'c:\test\workingGrid.csv')

    #oc.joingOp()
    pass


    #oc.listMatching("wicked tees")
    #oc.getMatching("887806214400")

