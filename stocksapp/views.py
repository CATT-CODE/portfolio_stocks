from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import timedelta
import random
from .models import Account, Positions, Transaction
from .forms import AccountForm
from .utils import get_or_none

now = timezone.now()

def charts(request):
	
	def newTicker(search=request.session['meta_data'] if 'meta_data' in request.session else random.choices(['GME', 'AAPL', 'AMZN', 'TSLA'])[0], start=now.date() - timedelta(days = 365), end=now.date()):
		search = search.upper()
		tickerInfo = yf.Ticker(search).info
		try: 
			currPrice = tickerInfo['currentPrice']
			percentChange = round((currPrice - tickerInfo['previousClose']) / tickerInfo['previousClose'] * 100, 2)
			request.session['meta_data'] = search
		except KeyError as e:
			currPrice = 0.00
			percentChange = 0.00
			messages.error(request, f"Enter valid ticker")


		
		if 'user' in request.session:
			a = get_or_none(Account, id=request.session['user'][2])
			if (q1 := get_or_none(Positions, account_id=request.session['user'][2], symbol=search)):
				p, avp = q1.shares, q1.avgPricePerShare 
			else: p, avp, th = 0, 0, [('N/A', now.date(), -0.1, 0.01)]
			th = [(row.symbol, row.timeDate.date(), row.shares, row.cashPrice) for row in qth] if (qth := Transaction.objects.filter(account=a).order_by('-timeDate').all()[:5]) else [('N/A', now.date(), -0.1, 0.01)]
			sharesGraph = [ ( row.symbol, row.shares, '{:,.2f}'.format(row.avgPricePerShare), ) for row in q] if (q := Positions.objects.filter(account_id=request.session['user'][2]).all()) else 'No Shares Available'
			# if sharesGraph != 'No Shares Available':
			# 	sharesGraph
			ab = a.cashBalance
		else: 
			p, avp, ab, th, sharesGraph = 0, 0, 0, [('N/A', now.date(), -0.1, 0.01)], 'No Shares Available'

		if request.POST.get('dayBttn'):
			tickerDF = yf.download(search, start=start, end=end, progress=False, interval='5m')
			layout = go.Layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgb(240,242,245)', font_family= 'verdana', xaxis_rangeslider_visible=False, title_text='Day', title_x=0.5)
		elif request.POST.get('weekBttn'): 
			tickerDF = yf.download(search, start=start, end=end, progress=False, interval='30m')
			layout = go.Layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgb(240,242,245)', font_family= 'verdana', xaxis_rangeslider_visible=False, title_text='Week', title_x=0.5)
		elif request.POST.get('monthBttn'): 
			tickerDF = yf.download(search, start=start, end=end, progress=False, interval='90m')
			layout = go.Layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgb(240,242,245)', font_family= 'verdana', xaxis_rangeslider_visible=False, title_text='Month', title_x=0.5)
		else: 
			layout = go.Layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgb(240,242,245)', font_family= 'verdana', xaxis_rangeslider_visible=False, title_text='Year', title_x=0.5)
			tickerDF = yf.download(search, start=start, end=end, progress=False)

			
		fig = go.Figure(data=[go.Candlestick(x=tickerDF.index, open=tickerDF.Open, high=tickerDF.High, low=tickerDF.Low, close=tickerDF.Close)], layout=layout)
		if request.POST.get('dayBttn') or request.POST.get('weekBttn'):
			fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"]), dict(bounds=[16, 9.5], pattern="hour")])
		elif request.POST.get('monthBttn'):
			fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"]),  dict(bounds=[14, 9.5], pattern="hour")])
		else:
			fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])])

		graph = fig.to_html(full_html=False, default_height=600, default_width='100%')

		context = {'graph': graph, 'tickerName': search, 'currentPrice': currPrice, 'percentChange': percentChange, 'sharesOwned': p, 'currCashValue': '${:,.2f}'.format(p*currPrice), 'cashBalance': '{:,.2f}'.format(ab), 'sharesGraph': sharesGraph, 'avgPrice': '${:,.2f}'.format(avp), 'transHist': th}

		return render(request, 'stocksapp/home.html', context)

	if request.method == 'POST':
		endDate = now.date()
		searchedTicker = request.session.get('meta_data')
		if request.POST.get('tickerSearch'):
			request.session['meta_data'] = request.POST.get('tickerSearch', None)
			return newTicker(request.POST.get('tickerSearch', None))
		elif request.POST.get('monthBttn'):
			return newTicker(searchedTicker, endDate - timedelta(days = 30), endDate)
		elif request.POST.get('weekBttn'):
			return newTicker(searchedTicker,  endDate - timedelta(days = 7), endDate)
		elif request.POST.get('dayBttn'):
			startDate = endDate - timedelta(days = 1)
			if endDate.isoweekday() == 7:
				startDate = endDate - timedelta(days = 2)
			elif endDate.isoweekday() == 1:
				startDate = endDate - timedelta(days = 3)
			print(startDate, endDate)
			return newTicker(searchedTicker, startDate, endDate)
		elif request.POST.get('sharesToBuy') or request.POST.get('sharesToSell'):
			return buySellBot(request, searchedTicker)

	return newTicker()
	

def signup(request):
		if 'user' in request.session:
			return redirect('stocksapp:charts')

		if request.method == 'POST':
			try:
				form = AccountForm(request.POST or None)
				if form.is_valid():
						form.save()
						request.session['cashBalance'] = '50,000.00'
						request.session['user'] = [form.cleaned_data.get('username'), form.cleaned_data.get('firstName').title(), Account.objects.get(username=form.cleaned_data.get('username')).id]
						return redirect('stocksapp:charts')
			except:
					form = AccountForm()
					return render(request, 'stocksapp/signup.html', {'form': form, 'msg': 'Username is not unique, try again!'})
		else:
				form = AccountForm()
		return render(request, 'stocksapp/signup.html', {'form': form})

def login(request):
	if 'user' in request.session:
		return redirect('stocksapp:charts')

	if request.method == 'POST':
		username = request.POST['username']
		try:
			u = Account.objects.get(username=username)
			if u.password == request.POST['password']:
				request.session['user'] = [username, u.firstName.title(), u.id]
				request.session['cashBalance'] = '{:,.2f}'.format(u.cashBalance)
				return redirect('stocksapp:charts')
		except (KeyError, Account.DoesNotExist):
			return render(request, 'stocksapp/login.html', {'msg': 'Username/password incorrect, try again.'})
	else:
		return render(request, 'stocksapp/login.html')

def logOut(request):
		try:
				logout(request)
		except KeyError:
				pass
		return HttpResponseRedirect(reverse('stocksapp:charts'))

def buySellBot(request, search):

	if 'user' in request.session:
		acct = request.session['user'][2]
		a = Account.objects.get(id=acct)
		currPrice = float(yf.Ticker(search).info['currentPrice'])

		if request.POST.get('sharesToBuy'):
			stb = float(request.POST.get('sharesToBuy'))
			try:

				if stb == 0.0:
					raise ValueError(f"Must buy more than 0 shares.")
				if a.cashBalance < currPrice * stb :
					raise ValueError(f"Attempt to buy more {search} than cash available, ${round(a.cashBalance, 2)}.")

				p,t = Positions.objects.get_or_create(
					account_id=acct,
					symbol = search,
					defaults={'avgPricePerShare': currPrice, 'shares': stb}
				)

				if not t:
					p.avgPricePerShare = (p.avgPricePerShare + currPrice) / 2
					p.shares = p.shares + stb
					p.save()
				print(p)
				a.cashBalance = a.cashBalance - (currPrice * stb)
				a.save()
				tb = Transaction.objects.create(account_id=acct, timeDate=now, symbol=search, shares=stb, buyOrSell='B', cashPrice=round(-currPrice * stb, 2))
				request.session['cashBalance'] = '{:,.2f}'.format(a.cashBalance)
				print(request.session['cashBalance'])
			except ValueError as e:
				messages.error(request, e)
				return redirect('stocksapp:charts')
			messages.success(request, f"Bought {request.POST.get('sharesToBuy')} shares of {search} for {round(currPrice * stb, 2)}!" )
			return redirect('stocksapp:charts')


		elif request.POST.get('sharesToSell'):
			sts = float(request.POST.get('sharesToSell'))
			try:
				p = Positions.objects.get(account_id=acct, symbol=search)
				if sts == 0.0:
					raise ValueError(request, f"Must sell more than 0 shares.")
				if p.shares < sts:
					raise ValueError(request, f"Attempt to sell more {search} than owned, {p.shares} shares.")

				elif p.shares == sts:
					a.cashBalance = a.cashBalance + (currPrice * sts)
					a.save()
					p.delete()
					messages.success(request, f"{request.POST.get('sharesToSell')} shares of {search} sold for ${round(currPrice * sts, 2)}. 0 shares left.")
					return redirect('stocksapp:charts')

				p.shares = p.shares - sts
				a.cashBalance = a.cashBalance + (currPrice * sts)
				p.save()
				a.save()

				tb = Transaction.objects.create(account_id=acct, timeDate=now, symbol=search, shares=-sts, buyOrSell='S', cashPrice=round(currPrice * sts, 2))
				request.session['cashBalance'] = '{:,.2f}'.format(a.cashBalance)
			except Positions.DoesNotExist:
				messages.error(request, f"No shares of {search} exist to sell.")
				return redirect('stocksapp:charts')
			except ValueError as e:
				messages.error(request, e)
				return redirect('stocksapp:charts')
			messages.success(request, f"Sold {request.POST.get('sharesToSell')} shares of {search} for ${tb.cashPrice}!" )
			return redirect('stocksapp:charts')


	else:
		messages.error(request, "Please login to Buy or Sell.")
		return redirect('stocksapp:charts')



	# return render(request, 'stocksapp/charts.html', context = {'currentPrice': currPrice})