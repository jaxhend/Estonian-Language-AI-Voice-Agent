import { useState } from "react";
import Navbar from "@/components/Navbar";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Calendar as CalendarComponent } from "@/components/ui/calendar";
import {
  Calendar,
  Clock,
  MapPin,
  User,
  Briefcase,
  CheckCircle2,
  XCircle,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { format, parse, isSameDay, addDays, startOfWeek, endOfWeek, eachDayOfInterval, isToday } from "date-fns";

interface Booking {
  id: number;
  name: string;
  service: string;
  time: string;
  location: string;
  status: "pending" | "confirmed" | "cancelled";
  date: string;
}

type CalendarView = "day" | "week" | "month";

const Admin = () => {
  const { toast } = useToast();
  const today = new Date();
  const tomorrow = addDays(today, 1);
  const nextWeek = addDays(today, 7);

  const [bookings, setBookings] = useState<Booking[]>([
    {
      id: 1,
      name: "John Doe",
      service: "Haircut",
      time: "2:00 PM",
      location: "Downtown Branch",
      status: "pending",
      date: format(tomorrow, "yyyy-MM-dd"),
    },
    {
      id: 2,
      name: "Jane Smith",
      service: "Consultation",
      time: "3:30 PM",
      location: "Main Office",
      status: "confirmed",
      date: format(today, "yyyy-MM-dd"),
    },
    {
      id: 3,
      name: "Bob Johnson",
      service: "Spa Treatment",
      time: "10:00 AM",
      location: "Wellness Center",
      status: "pending",
      date: format(tomorrow, "yyyy-MM-dd"),
    },
    {
      id: 4,
      name: "Alice Williams",
      service: "Massage",
      time: "2:00 PM",
      location: "Spa Branch",
      status: "confirmed",
      date: format(tomorrow, "yyyy-MM-dd"),
    },
    {
      id: 5,
      name: "Charlie Brown",
      service: "Dental Checkup",
      time: "9:00 AM",
      location: "Clinic A",
      status: "pending",
      date: format(nextWeek, "yyyy-MM-dd"),
    },
  ]);

  const [selectedDate, setSelectedDate] = useState<Date>(today);
  const [view, setView] = useState<CalendarView>("week");

  const handleStatusChange = (id: number, newStatus: "confirmed" | "cancelled") => {
    setBookings(bookings.map((booking) => (booking.id === id ? { ...booking, status: newStatus } : booking)));
    toast({
      title: `Booking ${newStatus}`,
      description: `Booking #${id} has been ${newStatus}.`,
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "confirmed":
        return "bg-success/20 text-success border-success/30";
      case "cancelled":
        return "bg-destructive/20 text-destructive border-destructive/30";
      case "pending":
        return "bg-accent/20 text-accent border-accent/30";
      default:
        return "bg-muted text-muted-foreground";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "confirmed":
        return CheckCircle2;
      case "cancelled":
        return XCircle;
      case "pending":
        return AlertCircle;
      default:
        return AlertCircle;
    }
  };

  const stats = {
    total: bookings.length,
    pending: bookings.filter((b) => b.status === "pending").length,
    confirmed: bookings.filter((b) => b.status === "confirmed").length,
    cancelled: bookings.filter((b) => b.status === "cancelled").length,
  };

  // Time slots from 9 AM to 5 PM
  const timeSlots = Array.from({ length: 9 }, (_, i) => {
    const hour = i + 9;
    return `${hour > 12 ? hour - 12 : hour}:00 ${hour >= 12 ? "PM" : "AM"}`;
  });

  // Get week range
  const weekStart = startOfWeek(selectedDate, { weekStartsOn: 1 });
  const weekEnd = endOfWeek(selectedDate, { weekStartsOn: 1 });
  const weekDays = eachDayOfInterval({ start: weekStart, end: weekEnd });

  // Get bookings for a specific date (exclude cancelled from calendar)
  const getBookingsForDate = (date: Date) => {
    return bookings.filter((b) => {
      const bookingDate = parse(b.date, "yyyy-MM-dd", new Date());
      return isSameDay(bookingDate, date) && b.status !== "cancelled";
    });
  };

  // Navigate dates
  const navigateDate = (direction: "prev" | "next") => {
    if (view === "day") {
      setSelectedDate(addDays(selectedDate, direction === "next" ? 1 : -1));
    } else if (view === "week") {
      setSelectedDate(addDays(selectedDate, direction === "next" ? 7 : -7));
    } else {
      setSelectedDate(addDays(selectedDate, direction === "next" ? 30 : -30));
    }
  };

  const goToToday = () => setSelectedDate(new Date());

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="max-w-7xl mx-auto p-6 space-y-6 animate-fade-in">
        <div>
          <h1 className="text-3xl font-bold text-foreground mb-2">Admin Dashboard</h1>
          <p className="text-muted-foreground">Manage and view all booking requests</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card className="p-4 shadow-[var(--shadow-card)]">
            <div className="text-sm text-muted-foreground">Total Bookings</div>
            <div className="text-2xl font-bold text-foreground mt-1">{stats.total}</div>
          </Card>
          <Card className="p-4 shadow-[var(--shadow-card)]">
            <div className="text-sm text-muted-foreground">Pending</div>
            <div className="text-2xl font-bold text-accent mt-1">{stats.pending}</div>
          </Card>
          <Card className="p-4 shadow-[var(--shadow-card)]">
            <div className="text-sm text-muted-foreground">Confirmed</div>
            <div className="text-2xl font-bold text-success mt-1">{stats.confirmed}</div>
          </Card>
          <Card className="p-4 shadow-[var(--shadow-card)]">
            <div className="text-sm text-muted-foreground">Cancelled</div>
            <div className="text-2xl font-bold text-destructive mt-1">{stats.cancelled}</div>
          </Card>
        </div>

        {/* Calendar View */}
        <Card className="shadow-[var(--shadow-card)]">
          {/* Calendar Header */}
          <div className="border-b p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Button variant="outline" size="sm" onClick={() => navigateDate("prev")}>
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <Button variant="outline" size="sm" onClick={goToToday}>
                  Today
                </Button>
                <Button variant="outline" size="sm" onClick={() => navigateDate("next")}>
                  <ChevronRight className="h-4 w-4" />
                </Button>
                <h2 className="text-lg font-semibold text-foreground">
                  {view === "week"
                    ? `${format(weekStart, "MMM d")} - ${format(weekEnd, "MMM d, yyyy")}`
                    : format(selectedDate, "MMMM yyyy")}
                </h2>
              </div>

              <div className="flex gap-1">
                <Button variant={view === "day" ? "default" : "outline"} size="sm" onClick={() => setView("day")}>
                  Day
                </Button>
                <Button variant={view === "week" ? "default" : "outline"} size="sm" onClick={() => setView("week")}>
                  Week
                </Button>
                <Button variant={view === "month" ? "default" : "outline"} size="sm" onClick={() => setView("month")}>
                  Month
                </Button>
              </div>
            </div>
          </div>

          {/* Calendar Grid */}
          <div className="overflow-x-auto">
            {view === "week" && (
              <div className="min-w-[800px]">
                {/* Week headers */}
                <div className="grid grid-cols-[60px,repeat(7,1fr)] border-b">
                  <div className="p-2"></div>
                  {weekDays.map((day) => (
                    <div
                      key={day.toISOString()}
                      className={`p-2 text-center text-sm ${isToday(day) ? "bg-primary/10" : ""}`}
                    >
                      <div className={`font-semibold ${isToday(day) ? "text-primary" : "text-foreground"}`}>
                        {format(day, "EEE")}
                      </div>
                      <div className={`text-xs ${isToday(day) ? "text-primary" : "text-muted-foreground"}`}>
                        {format(day, "d")}
                      </div>
                    </div>
                  ))}
                </div>

                {/* Time slots */}
                <div className="relative">
                  {timeSlots.map((time, idx) => (
                    <div
                      key={time}
                      className="grid grid-cols-[60px,repeat(7,1fr)] border-b"
                      style={{ minHeight: "60px" }}
                    >
                      <div className="p-2 text-xs text-muted-foreground text-right pr-3 border-r">{time}</div>
                      {weekDays.map((day) => {
                        const dayBookings = getBookingsForDate(day).filter((b) => b.time === time);
                        return (
                          <div
                            key={`${day.toISOString()}-${time}`}
                            className="border-r p-1 hover:bg-accent/5 transition-colors"
                          >
                            {dayBookings.map((booking) => (
                              <div
                                key={booking.id}
                                className={`p-2 rounded text-xs cursor-pointer ${
                                  booking.status === "confirmed"
                                    ? "bg-success text-white border border-success"
                                    : booking.status === "pending"
                                      ? "bg-accent/30 border border-accent/50"
                                      : "bg-destructive/20 border border-destructive/40"
                                }`}
                              >
                                <div className="font-medium truncate">{booking.name}</div>
                                <div className="text-[10px] opacity-80 truncate">{booking.service}</div>
                              </div>
                            ))}
                          </div>
                        );
                      })}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {view === "day" && (
              <div>
                {timeSlots.map((time) => {
                  const dayBookings = getBookingsForDate(selectedDate).filter((b) => b.time === time);
                  return (
                    <div key={time} className="flex border-b" style={{ minHeight: "60px" }}>
                      <div className="w-20 p-2 text-xs text-muted-foreground text-right border-r">{time}</div>
                      <div className="flex-1 p-2 hover:bg-accent/5 transition-colors">
                        {dayBookings.map((booking) => (
                          <div
                            key={booking.id}
                            className={`p-2 rounded text-sm mb-1 ${
                              booking.status === "confirmed"
                                ? "bg-success text-white border border-success"
                                : booking.status === "pending"
                                  ? "bg-accent/30 border border-accent/50"
                                  : "bg-destructive/20 border border-destructive/40"
                            }`}
                          >
                            <div className="font-medium">{booking.name}</div>
                            <div className="text-xs opacity-80">
                              {booking.service} • {booking.location}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {view === "month" && (
              <div className="p-4">
                <CalendarComponent
                  mode="single"
                  selected={selectedDate}
                  onSelect={(date) => date && setSelectedDate(date)}
                  className="pointer-events-auto mx-auto"
                  modifiers={{
                    pending: bookings
                      .filter((b) => b.status === "pending")
                      .map((b) => parse(b.date, "yyyy-MM-dd", new Date())),
                    confirmed: bookings
                      .filter((b) => b.status === "confirmed")
                      .map((b) => parse(b.date, "yyyy-MM-dd", new Date())),
                  }}
                  modifiersClassNames={{
                    pending: "relative after:absolute after:bottom-1 after:right-3 after:w-1 after:h-1 after:rounded-full after:bg-accent",
                    confirmed: "relative before:absolute before:bottom-1 before:left-3 before:w-1 before:h-1 before:rounded-full before:bg-success",
                  }}
                />
              </div>
            )}
          </div>
        </Card>

        {/* Bookings List */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-foreground">Pending Bookings</h2>
          <div className="grid gap-4">
            {bookings
              .filter((b) => b.status === "pending")
              .map((booking) => {
                const StatusIcon = getStatusIcon(booking.status);
                return (
                  <Card
                    key={booking.id}
                    className="p-6 shadow-[var(--shadow-card)] hover:shadow-[var(--shadow-soft)] transition-shadow"
                  >
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                      <div className="flex-1 space-y-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <h3 className="text-lg font-semibold text-foreground">{booking.name}</h3>
                            <Badge className={`${getStatusColor(booking.status)} border`}>
                              <StatusIcon className="h-3 w-3 mr-1" />
                              {booking.status}
                            </Badge>
                          </div>
                          <span className="text-sm text-muted-foreground">
                            {format(parse(booking.date, "yyyy-MM-dd", new Date()), "MMM d, yyyy")}
                          </span>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                          <div className="flex items-center gap-2 text-muted-foreground">
                            <Briefcase className="h-4 w-4 text-primary" />
                            {booking.service}
                          </div>
                          <div className="flex items-center gap-2 text-muted-foreground">
                            <Clock className="h-4 w-4 text-primary" />
                            {booking.time}
                          </div>
                          <div className="flex items-center gap-2 text-muted-foreground">
                            <MapPin className="h-4 w-4 text-primary" />
                            {booking.location}
                          </div>
                          <div className="flex items-center gap-2 text-muted-foreground">
                            <User className="h-4 w-4 text-primary" />
                            ID: #{booking.id}
                          </div>
                        </div>
                      </div>

                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          onClick={() => handleStatusChange(booking.id, "confirmed")}
                          className="bg-success hover:bg-success/90"
                        >
                          <CheckCircle2 className="h-4 w-4 mr-1" />
                          Confirm
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleStatusChange(booking.id, "cancelled")}
                          className="border-destructive text-destructive hover:bg-destructive/10"
                        >
                          <XCircle className="h-4 w-4 mr-1" />
                          Cancel
                        </Button>
                      </div>
                    </div>
                  </Card>
                );
              })}
            {bookings.filter((b) => b.status === "pending").length === 0 && (
              <Card className="p-8 text-center">
                <p className="text-muted-foreground">No pending bookings</p>
              </Card>
            )}
          </div>
        </div>

        {/* Cancelled Bookings Log */}
        {bookings.filter((b) => b.status === "cancelled").length > 0 && (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-foreground">Cancelled Bookings</h2>
            <div className="grid gap-3">
              {bookings
                .filter((b) => b.status === "cancelled")
                .map((booking) => (
                  <Card key={booking.id} className="p-4 shadow-[var(--shadow-card)] opacity-75">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h3 className="font-semibold text-foreground">{booking.name}</h3>
                          <Badge className={`${getStatusColor(booking.status)} border text-xs`}>
                            <XCircle className="h-3 w-3 mr-1" />
                            Cancelled
                          </Badge>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <Calendar className="h-3 w-3" />
                            {format(parse(booking.date, "yyyy-MM-dd", new Date()), "MMM d, yyyy")}
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {booking.time}
                          </span>
                          <span className="flex items-center gap-1">
                            <Briefcase className="h-3 w-3" />
                            {booking.service}
                          </span>
                          <span className="flex items-center gap-1">
                            <MapPin className="h-3 w-3" />
                            {booking.location}
                          </span>
                        </div>
                      </div>
                    </div>
                  </Card>
                ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Admin;
