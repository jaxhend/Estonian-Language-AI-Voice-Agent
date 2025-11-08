import Navbar from "@/components/Navbar";
import { Card } from "@/components/ui/card";
import { Calendar, CheckCircle2, Clock, TrendingUp, Users, DollarSign } from "lucide-react";
import { ChartContainer, ChartTooltip, ChartTooltipContent, ChartLegend, ChartLegendContent } from "@/components/ui/chart";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Legend, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { ChartConfig } from "@/components/ui/chart";

const Analytics = () => {
  const stats = [
    { label: "Total Bookings", value: "127", icon: Calendar, color: "text-primary" },
    { label: "Completed", value: "98", icon: CheckCircle2, color: "text-success" },
    { label: "Active Users", value: "45", icon: Users, color: "text-secondary" },
    { label: "Avg Response Time", value: "1.2s", icon: Clock, color: "text-accent" },
  ];

  const monthlyData = [
    { month: "Jan", bookings: 45, revenue: 4500 },
    { month: "Feb", bookings: 52, revenue: 5200 },
    { month: "Mar", bookings: 61, revenue: 6100 },
    { month: "Apr", bookings: 70, revenue: 7000 },
    { month: "May", bookings: 85, revenue: 8500 },
    { month: "Jun", bookings: 92, revenue: 9200 },
  ];

  const topServices = [
    { name: "Haircut", bookings: 45, percentage: 35, fill: "hsl(var(--primary))" },
    { name: "Spa Treatment", bookings: 38, percentage: 30, fill: "hsl(var(--secondary))" },
    { name: "Massage", bookings: 25, percentage: 20, fill: "hsl(var(--accent))" },
    { name: "Consultation", bookings: 19, percentage: 15, fill: "hsl(var(--success))" },
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
  } satisfies ChartConfig;

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="max-w-7xl mx-auto p-6 space-y-6 animate-fade-in">
        <div>
          <h1 className="text-3xl font-bold text-foreground mb-2">Analytics & Insights</h1>
          <p className="text-muted-foreground">Track performance and booking trends</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {stats.map((stat) => (
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
              <h2 className="text-xl font-semibold text-foreground">Monthly Booking Trends</h2>
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
              <h2 className="text-xl font-semibold text-foreground">Revenue Trends</h2>
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
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-muted-foreground">Booking Completion</span>
                  <span className="font-medium text-foreground">92%</span>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-primary to-secondary w-[92%]" />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-muted-foreground">AI Confidence Score</span>
                  <span className="font-medium text-foreground">96%</span>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-primary to-secondary w-[96%]" />
                </div>
              </div>
            </div>
          </Card>

          <Card className="p-6 shadow-[var(--shadow-card)]">
            <h2 className="text-xl font-semibold mb-4 text-foreground">Top Services</h2>
            <ChartContainer config={servicesChartConfig} className="h-64 w-full">
              <PieChart>
                <ChartTooltip 
                  content={<ChartTooltipContent />}
                  formatter={(value, name, props) => `${props.payload.bookings} bookings (${props.payload.percentage}%)`}
                />
                <Pie
                  data={topServices}
                  dataKey="bookings"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={2}
                  label={({ name, percentage }) => `${name} (${percentage}%)`}
                  labelLine={false}
                >
                  {topServices.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
              </PieChart>
            </ChartContainer>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
