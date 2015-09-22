#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# author  : Prithwish Chakraborty <prithwi@vt.edu>
# license : MIT
# date    : 2012-01-01
"""
Module to convert calendar dates to epiweek and vice-versa.

**Epiweek Definition**:
[Source](http://www.cmmcp.org/epiweek.htm)

> The first epi week of the year ends, by definition, on the first Saturday of
> January, as long as it falls at least four days into the month. Each epi week
> begins on a Sunday and ends on a Saturday.
"""

import datetime 
from dateutil.relativedelta import relativedelta, WE, SU
import functools

import logging 
log = logging.getLogger()


class EwDateConverter(object):
    """Base class to encode EW definition and provide routins to convert between
    (year, eweek) and (date)
    """
    @staticmethod
    def first_ew_sunday(year):
        """Function to calculate first Sunday of a year satisfying EW defintion.

        :year: year to calculate first EW for (int)

        :returns: sunday of first EW
        """
        dt = datetime.date(year, 1, 1)  # Finding Jan 1 of year

        # Finding first wednessday of calendar year
        first_wednesday = dt + relativedelta(weekday=WE(+1))

        # Finding Sunday of the week containing the first wednesday
        # --------------------------------------------------------
        # Effectively finding first week where Saturday is atleast 4 days 
        # into the calendar year
        first_sunday = first_wednesday + relativedelta(weekday=SU(-1))
        return first_sunday

    @staticmethod
    def convertToEw(dt):
        """converts a date object to (year, ew) tuple

        :dt: date object
        """
        year = dt.year
        # For this year
        # ------------
        # first sunday of the year
        ft_sunday = EwDateConverter.first_ew_sunday(year)   
        # last saturday of year
        lt_saturday = (EwDateConverter.first_ew_sunday(year + 1) 
                       + datetime.timedelta(days=-1))

        if dt < ft_sunday: 
            # date falls in previous year
            year -= 1
            ft_sunday = EwDateConverter.first_ew_sunday(year)
        elif dt > lt_saturday:
            # date falls in next year
            year += 1
            ft_sunday = EwDateConverter.first_ew_sunday(year)

        week = (dt - ft_sunday).days // 7 + 1
        return (year, week)

    @staticmethod
    def convertToDate(eweek):
        """converts a (year, ew) tuple to the sunday of the implied week

        :eweek: int, int
        """
        year, week = eweek
        ft_sunday = EwDateConverter.first_ew_sunday(year)
        dt = ft_sunday + datetime.timedelta(weeks=week - 1)
        return dt


@functools.total_ordering
class EwDate(EwDateConverter):
    """Class to extend functionalities of EwDateConverter.

    Defines EwDate object
    Provides routines to initialize, add, subtract EwDate.

    Experimental: eweek and date are linked. Implemented through propertis.
    """

    def __init__(self, act_date=None, **kwargs):
        """EwDate Object. 
        
        Can return initialized EwDate if 'fmt' and 's' specified. If either not 
        specified empty Object returned.

        :act_date: actual date
        
        :kwargs:
        Implemented kwargs

            :fmt: format of string. 'date' or 'week'
            :s: string to initialize with. 
                Expects
                a) for fmt = 'date': YYYY-mm-dd (or date/datetime/pd timestamp)
                b) for fmt = 'w' : YYYY-ww (or tuple year, week)


        :returns: EwDate object
        """
        EwDateConverter.__init__(self)

        fmt = kwargs.pop('fmt', None)
        s = kwargs.pop('s', None)

        if fmt is not None and s is not None:
            # fmt and string is not empty. Try to initialize a ewDate
            _eweek, act_date = self._create_EwDate(fmt, s, **kwargs)

            self.eweek = _eweek  # setter also sets self.date

        self.act_date = act_date
        return
        
    def _create_EwDate(self, fmt, s, **kwargs):
        """fills out ewDate object.
        """
        if fmt == 'date':
            # assuming s is a date/datetime/pandas datetime/string
            # if string YYYY-mm-dd
            try:
                if type(s) is datetime.date:
                    act_date = s
                elif hasattr(s, 'date'):
                    if callable(getattr(s, 'date')):
                        act_date = s.date()
                    else:
                        act_date = s.date
                elif hasattr(s, 'to_datetime') and callable(getattr(s, 'date')):
                    act_date = s.to_datetime().date()
                else:
                    act_date = datetime.datetime.strptime(s, '%Y-%m-%d').date()
                # Finding the week number
                eweek = EwDate.convertToEw(act_date)
            except Exception as e:
                raise Exception('Input not compatible with fmt=YYYY-mm-dd: {0}'
                                .format(e))
        elif fmt == 'week':
            # assuming a week data for s
            # either YYYY-ww format or a tuple of ints
            try:
                if type(s) is str:
                    ss = s.strip().split('-')
                    eweek = (datetime.datetime.strptime(ss[0], '%Y').year, int(ss[1]))
                else:
                    eweek = tuple(s)
                act_date = EwDate.convertToDate(eweek)
            except Exception as e:
                raise Exception(u'Input not compatible with fmt=YYYY-ww: {0}'
                                .format(e))
        else:
            raise ValueError('fmt can only be date/week')
        return eweek, act_date

    # ********************************************************
    #           LINKED ATTRIBUTES: eweek and date
    def eweek():
        doc = "eweek property."

        def fget(self):
            try:
                return self._eweek
            except:
                return None

        def fset(self, value):
            self._eweek = value
            self._date = EwDate.convertToDate(value)

        def fdel(self):
            del self._eweek
            del self._date
        return locals()
    eweek = property(**eweek())

    def date():
        doc = "the date property"

        def fget(self):
            try:
                return self._date
            except:
                return None

        def fset(self, value):
            self._date = value
            self._eweek = EwDate.convertToEw(value)

        def fdel(self):
            del self._date
            del self._eweek
        return locals()
    date = property(**date())

    @property
    def rep_date(self):
        if self.date:
            return self.date + relativedelta(weekday=WE(+1))
        else:
            return None

    # ******************************************************

    def __repr__(self):
        """For printing purposes
        """
        s = ("act_date={0}, date={1}, eweek={2}"
             .format(self.act_date, self.date, self.eweek))
        return u'{}({})'.format(self.__class__.__name__, s)

    # ----------------------------------------------
    #                MATH ROUTINES
    def __add__(self, delta):
        """Add delta to EwDate object

        :delta: any timedelta object
        """
        try:
            result = EwDate()
            result.date = self.date + delta
        except Exception, e:
            raise Exception('exception while adding: %s' % e)
        return result

    def __sub__(self, another_EwDate):
        """Substract a EwDate

        :another_EwDate: EwDate object.
        """
        try:
            delta = self.date - another_EwDate.date
        except Exception, e:
            raise Exception('exception while adding: %s' % e)
        return delta

    # -------------------------------------------------------
    #                  Boolean Routines
    def __lt__(self, another_EwDate):
        return (self.date < another_EwDate.date)

    def __eq__(self, another_EwDate):
        return (self.date == another_EwDate.date)
