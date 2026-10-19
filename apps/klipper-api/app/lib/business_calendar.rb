require "date"

module BusinessCalendar
  FIXED_HOLIDAYS = [ [ 1, 1 ], [ 4, 21 ], [ 5, 1 ], [ 9, 7 ], [ 10, 12 ], [ 11, 2 ], [ 11, 15 ], [ 12, 25 ] ].freeze

  module_function

  def easter(year)
    a = year % 19
    b = year / 100
    c = year % 100
    d = b / 4
    e = b % 4
    f = (b + 8) / 25
    g = (b - f + 1) / 3
    h = (19 * a + b - d - g + 15) % 30
    i = c / 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) / 451
    month = (h + l - 7 * m + 114) / 31
    day = (h + l - 7 * m + 114) % 31 + 1

    Date.new(year, month, day)
  end

  def business_day?(date)
    !date.saturday? && !date.sunday? && !holiday?(date)
  end

  def next_business_day(date)
    candidate = date + 1
    candidate += 1 until business_day?(candidate)
    candidate
  end

  def holiday?(date)
    fixed_holiday?(date) || movable_holiday?(date)
  end
  private_class_method :holiday?

  def fixed_holiday?(date)
    FIXED_HOLIDAYS.include?([ date.month, date.day ]) || black_awareness_day?(date)
  end
  private_class_method :fixed_holiday?

  def black_awareness_day?(date)
    date.year >= 2024 && date.month == 11 && date.day == 20
  end
  private_class_method :black_awareness_day?

  def movable_holiday?(date)
    easter_sunday = easter(date.year)
    [ easter_sunday - 48, easter_sunday - 47, easter_sunday - 2, easter_sunday + 60 ].include?(date)
  end
  private_class_method :movable_holiday?
end
