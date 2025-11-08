import { useState, useEffect } from "react";
import Navbar from "@/components/Navbar";
import { Card } from "@/components/ui/card";
import { Calendar, CheckCircle2, Clock, TrendingUp, Users, DollarSign, Bot, PieChart as PieIcon } from "lucide-react";
import { ChartContainer, ChartTooltip, ChartTooltipContent, ChartLegend, ChartLegendContent } from "@/components/ui/chart";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Legend, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { ChartConfig } from "@/components/ui/chart";

const API_URL = "http://127.0.0.1:8000/api";

const Analytics = () => {
  const [stats, setStats] = useState({ total_bookings: 0, completed_bookings: 0, active_users: 0, avg_response_time: "0s" });
  const [monthlyData, setMonthlyData] = useState([]);
  const [topServices, setTopServices] = useState([]);
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAllData = async () => {
      setLoading(true);
      try {
        const [statsRes, monthlyRes, topServicesRes, summaryRes] = await Promise.all([
          fetch(`${API_URL}/analytics/booking-stats`),
          fetch(`${API_URL}/analytics/monthly-trends`),
          fetch(`${API_URL}/analytics/top-services`),
          fetch(`${API_URL}/analytics/summary`),
        ]);

        const statsData = await statsRes.json();
        const monthlyData = await monthlyRes.json();
        const topServicesData = await topServicesRes.json();
        const summaryData = await summaryRes.json();

        setStats(statsData);
        setMonthlyData(monthlyData);
        setTopServices(topServicesData.map((s: any, i: number) => ({
          ...s,
          fill: ["hsl(var(--primary))", "hsl(var(--secondary))", "hsl(var(--accent))", "hsl(var(--success))"][i % 4]
        })));
        setSummary(summaryData.summary);

      } catch (error) {
        console.error("Failed to fetch analytics data:", error);
        setSummary("Failed to load analytics data.");
      } finally {
        setLoading(false);
      }
    };

    fetchAllData();
  }, []);

  const statCards = [
    { label: "Total Bookings", value: stats.total_bookings, icon: Calendar, color: "text-primary" },
    { label: "Completed", value: stats.completed_bookings, icon: CheckCircle2, color: "text-success" },
    { label: "Active Users", value: stats.active_users, icon: Users, color: "text-secondary" },
    { label: "Avg Conversation Time", value: stats.avg_response_time, icon: Clock, color: "text-accent" },
  ];

  const bookingChartConfig = {
    bookings: {
      label: "Bookings",
      color: "hsl(var(--primary))",
    },
  } satisfies ChartConfig;

  const revenueChartConfig = {
    revenue: {
      label: "Revenue",
      color: "hsl(var(--success))",
    },
  } satisfies ChartConfig;

  const servicesChartConfig = {
    bookings: {
      label: "Bookings",
    },
    ...Object.fromEntries(topServices.map((s: any) => [s.name, { label: s.name, color: s.fill }]))
  } satisfies ChartConfig;

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="max-w-7xl mx-auto p-6 space-y-6 animate-fade-in">
        <div>
          <h1 className="text-3xl font-bold text-foreground mb-2">Analytics & Insights</h1>
          <p className="text-muted-foreground">Track performance and booking trends</p>
        </div>

        {/* AI Summary Card */}
        <Card className="p-6 shadow-[var(--shadow-card)] bg-gradient-to-br from-primary/10 to-background">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-foreground">AI-Generated Summary</h2>
            <Bot className="h-6 w-6 text-primary" />
          </div>
          {loading ? (
            <div className="space-y-2">
              <div className="h-4 bg-muted rounded w-3/4 animate-pulse"></div>
              <div className="h-4 bg-muted rounded w-1/2 animate-pulse"></div>
            </div>
          ) : (
            <div className="text-foreground/90 whitespace-pre-wrap">{summary}</div>
          )}
        </Card>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {statCards.map((stat) => (
            <Card key={stat.label} className="p-6 shadow-[var(--shadow-card)] hover:shadow-[var(--shadow-soft)] transition-shadow">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">{stat.label}</p>
                  <h3 className="text-3xl font-bold mt-2 text-foreground">{stat.value}</h3>
                </div>
                <stat.icon className={`h-8 w-8 ${stat.color}`} />
              </div>
            </Card>
          ))}
        </div>

        {/* Charts Section */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Booking Trends Chart */}
          <Card className="p-6 shadow-[var(--shadow-card)]">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-foreground">Monthly Booking Trends (2025)</h2>
              <TrendingUp className="h-5 w-5 text-success" />
            </div>
            <ChartContainer config={bookingChartConfig} className="h-64 w-full">
              <AreaChart data={monthlyData}>
                <defs>
                  <linearGradient id="bookingGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0.1}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="month" className="text-xs" />
                <YAxis className="text-xs" />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Area 
                  type="monotone" 
                  dataKey="bookings" 
                  stroke="hsl(var(--primary))" 
                  fillOpacity={1}
                  fill="url(#bookingGradient)"
                />
              </AreaChart>
            </ChartContainer>
          </Card>

          {/* Revenue Chart */}
          <Card className="p-6 shadow-[var(--shadow-card)]">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-foreground">Revenue Trends (2025)</h2>
              <DollarSign className="h-5 w-5 text-success" />
            </div>
            <ChartContainer config={revenueChartConfig} className="h-64 w-full">
              <BarChart data={monthlyData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="month" className="text-xs" />
                <YAxis className="text-xs" />
                <ChartTooltip 
                  content={<ChartTooltipContent />}
                  formatter={(value) => `$${value}`}
                />
                <Bar 
                  dataKey="revenue" 
                  fill="hsl(var(--success))" 
                  radius={[8, 8, 0, 0]}
                />
              </BarChart>
            </ChartContainer>
          </Card>
        </div>

        {/* Performance Metrics & Top Services */}
        <div className="grid lg:grid-cols-2 gap-6">
          <Card className="p-6 shadow-[var(--shadow-card)]">
            <h2 className="text-xl font-semibold mb-6 text-foreground">Performance Metrics</h2>
            <div className="space-y-4">
              {/* Mocked data for now */}
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-muted-foreground">Customer Satisfaction</span>
                  <span className="font-medium text-foreground">94%</span>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-primary to-secondary w-[94%]" />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-muted-foreground">Response Accuracy</span>
                  <span className="font-medium text-foreground">88%</span>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-primary to-secondary w-[88%]" />
                </div>
              </div>
            </div>
          </Card>

          <Card className="p-6 shadow-[var(--shadow-card)]">
            <h2 className="text-xl font-semibold mb-4 text-foreground">Top Services</h2>
            <ChartContainer config={servicesChartConfig} className="h-64 w-full">
              <PieChart>
                <ChartTooltip content={<ChartTooltipContent nameKey="bookings" hideLabel />} />
                <Pie data={topServices} dataKey="bookings" nameKey="name" innerRadius={50}>
                  {topServices.map((entry: any) => (
                    <Cell key={`cell-${entry.name}`} fill={entry.fill} />
                  ))}
                </Pie>
                <ChartLegend content={<ChartLegendContent nameKey="name" />} />
              </PieChart>
            </ChartContainer>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
