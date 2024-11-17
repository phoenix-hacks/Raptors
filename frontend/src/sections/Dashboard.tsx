import React, { useState, useEffect } from 'react';
import { useTheme } from '@/Context/ThemeContext';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';
import {
    PieChart,
    Pie,
    Cell,
    Tooltip,
    RadarChart,
    PolarGrid,
    PolarAngleAxis,
    PolarRadiusAxis,
    Radar,
    Bar,
    XAxis,
    YAxis,
    Legend,
    BarChart,
    ResponsiveContainer,
} from 'recharts';
import { getLatestAnalytics, getAnalyticsHistory } from '@/lib/analytics-service';
import {
    Sheet,
    SheetTrigger,
    SheetContent,
    SheetHeader,
    SheetTitle,
} from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';
import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
} from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { LayoutDashboard, X, Truck, Package, AlertTriangle, Boxes } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface Metrics {
    [key: string]: number | string;
}

interface Prediction {
    predicted_score: number;
    feature_importances: {
        [key: string]: number;
    };
    alternative_modes: string[];
    estimated_savings: number;
}

interface ProcessedData {
    transport_mode: string;
    [key: string]: string | number | any[];
}

interface SustainabilityAnalysis {
    metrics: Metrics;
    overall_sustainability_score: number;
    predictions: Prediction;
    processed_data: {
        [x: string]: any;
        processed_data: ProcessedData;
    };
}

interface Result {
    processed_data: any;
    shipment_id: string;
    llm_insights: string;
    sustainability_analysis: SustainabilityAnalysis;
}

interface SustainabilityAnalytics {
    timestamp: string;
    num_shipments_analyzed: number;
    results: Result[];
}

interface KpiCardPropsType {
    title: string;
    value: string;
    icon: React.ReactNode;
    description?: string;
}

const KpiCard: React.FC<KpiCardPropsType> = ({
    title,
    value,
    icon,
}) => {
    const { theme } = useTheme();
    return (
        <Card className={`${theme === 'dark' ? 'bg-black' : 'bg-white'}  rounded-none`}>
            <CardContent className="p-6">
                <div className="flex justify-between items-center mb-4">
                    <span className={`${theme === 'dark' ? 'text-white' : 'text-black'} `}>{icon}</span>
                    <h3 className={`text-sm font-medium ${theme === 'dark' ? 'text-white' : 'text-black'} `}>{title}</h3>
                </div>
                <div className="space-y-1">
                    <p className={`text-2xl font-semibold ${theme === 'dark' ? 'text-white' : 'text-black'} `}>{value}</p>
                </div>
            </CardContent>
        </Card>
    );
};

interface ShippingKpiCardsProps {
    shipmentId: string;
    transportMode: string;
    overallSustainabilityScore: number;
    materialType: string;
}

const ShippingKpiCards: React.FC<ShippingKpiCardsProps> = ({
    shipmentId,
    transportMode,
    overallSustainabilityScore,
    materialType,
}) => {
    const data = [
        {
            title: 'Shipment ID',
            value: shipmentId,
            icon: <Package className="h-6 w-6" />,
        },
        {
            title: 'Shipment Mode',
            value: transportMode,
            icon: <Truck className="h-6 w-6" />,
        },
        {
            title: 'Overall Sustainability Score',
            value: overallSustainabilityScore.toFixed(2),
            icon: <AlertTriangle className="h-6 w-6" />,
        },
        {
            title: 'Material Type',
            value: materialType,
            icon: <Boxes className="h-6 w-6" />,
        },
    ];

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-10 mb-10">
            {data.map((item, index) => (
                <KpiCard
                    key={index}
                    title={item.title}
                    value={item.value}
                    icon={item.icon}
                />
            ))}
        </div>
    );
};

interface ChartData {
    sustainabilityScores: Array<{
        name: string;
        actual: number;
        predicted: number;
    }>;
    pieData: Array<{
        name: string;
        value: number;
    }>;
    radarData: Array<{
        subject: string;
        importance: number;
    }>;
    sustainabilityMetrics: Array<{
        timestamp: string;
        carbon_footprint: number;
        energy_efficiency: number;
        resource_efficiency: number;
        waste_reduction: number;
    }>;
}

const ShipmentSelector: React.FC<{
    shipments: string[];
    selectedId: string | null;
    onSelect: (id: string) => void;
}> = ({ shipments, selectedId, onSelect }) => {
    const { theme } = useTheme();
    return (
        <select
            value={selectedId || ''}
            onChange={(e) => onSelect(e.target.value)}
            className={`p-2 border ${theme === 'dark' ? 'bg-black text-white' : 'bg-white text-black'} w-full cursor-pointer focus:border-primary [&>option]:${theme === 'dark' ? 'bg-black' : 'bg-white'} `}
        >
            {shipments.map((id) => (
                <option key={id} value={id}>
                    {id}
                </option>
            ))}
        </select>
    );
};

const ChartWrapper: React.FC<{ title: string; children: React.ReactNode }> = ({
    title,
    children,

}) => {
    const { theme } = useTheme();
    return (
        <div className={`${theme === 'dark' ? 'bg-black' : 'bg-white'}  p-4 border`}>
            <h4 className={`${theme === 'dark' ? 'text-white' : 'text-black'}  mb-4 text-lg font-medium`}>{title}</h4>
            <div className="flex justify-center items-center">{children}</div>
        </div>
    )
};

export const Dashboard: React.FC = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [latestData, setLatestData] = useState<SustainabilityAnalytics | null>(
        null);
    const [historyData, setHistoryData] = useState<SustainabilityAnalytics[]>(
        []);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [chartData, setChartData] = useState<ChartData | null>(null);

    const [selectedShipmentId, setSelectedShipmentId] = useState<string | null>(
        null);
    const [availableShipments, setAvailableShipments] = useState<string[]>([]);
    const [score, setScore] = useState<number>(0);
    const selectedShipmentData = latestData?.results?.find(
        (result) => result.shipment_id === selectedShipmentId);

    const fetchData = async () => {
        setLoading(true);
        setError(null);
        try {
            const latest = await getLatestAnalytics();
            setLatestData(latest);

            if (latest?.results) {
                const shipmentIds = latest.results.map((r: { shipment_id: any; }) => r.shipment_id);
                setAvailableShipments(shipmentIds);
                setSelectedShipmentId(shipmentIds[0]);
            }
            const history = await getAnalyticsHistory();
            setHistoryData(history);
        } catch (err) {
            setError('Failed to load analytics data');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (isOpen && !latestData) {
            fetchData();
        }
    }, [isOpen]);
    interface ScoreDonutChartProps {
        score: number;
        label: string;
        textColor?: string;
    }
    const ScoreDonutChart: React.FC<{ score: number; label: string; textColor?: string }> = ({ score, label, textColor }) => {
        const [value, setValue] = useState(0);
        const percentage = Math.min(Math.max(score, 0), 100);
        const intervalTime = 20;
        const duration = 2000;
        const increment = percentage / (duration / intervalTime);

        useEffect(() => {
            let startValue = 0;
            const timer = setInterval(() => {
                startValue += increment;
                if (startValue >= percentage) {
                    startValue = percentage;
                    clearInterval(timer);
                }
                setValue(startValue);
            }, intervalTime);

            return () => clearInterval(timer);
        }, [percentage, increment]);

        const gradientId = `gradient-${label.replace(/\s+/g, '-')}`;

        return (
            <div className="relative w-48 h-48">
                <svg style={{ height: 0 }}>
                    <defs>
                        <linearGradient id={gradientId}>
                            <stop offset="0%" stopColor="#ff4e50" />
                            <stop offset="100%" stopColor="#1fa2ff" />
                        </linearGradient>
                    </defs>
                </svg>
                <svg style={{ height: 0 }}>
                    <defs>
                        <linearGradient id={gradientId}>
                            <stop offset="0%" stopColor="#ff4e50" />
                            <stop offset="100%" stopColor="#1fa2ff" />
                        </linearGradient>
                    </defs>
                </svg>
                <CircularProgressbar
                    value={value}
                    styles={buildStyles({
                        rotation: 0.75,
                        strokeLinecap: 'round',
                        trailColor: '#eee',
                        pathColor: `url(#${gradientId})`,
                        textColor: textColor
                    })}
                />
                <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                    <div className="text-2xl font-bold" style={{ color: textColor }}>
                        {Math.round(value)}%
                    </div>
                    <div className="text-sm mt-1" style={{ color: textColor }}>
                        {label}
                    </div>
                </div>
            </div>
        );
    };
    const [sustainabilityScores, setSustainabilityScores] = useState<Array<{
        name: string;
        actual: number;
        predicted: number;
    }>>([]);
    const processChartData = (
        latestAnalytics: SustainabilityAnalytics | null,
        historyAnalytics: SustainabilityAnalytics[],
        shipmentId: string | null
    ): ChartData | null => {
        if (!latestAnalytics || !shipmentId) return null;
        const results = Array.isArray(latestAnalytics.results)
            ? latestAnalytics.results
            : [latestAnalytics.results];

        const shipmentData = results.find(
            (result) => result.shipment_id === shipmentId
        );

        if (!shipmentData) return null;
        const metrics = shipmentData.sustainability_analysis.predictions.feature_importances;

        const pieData = Object.entries(metrics)
            .filter(
                ([key, value]) =>
                    typeof value === 'number' &&
                    !['distance', 'carbon_emissions'].includes(key)
            )
            .map(([key, value]) => ({
                name: key
                    .split('_')
                    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(' '),
                value: Number((Number(value) * 100).toFixed(2)),
            }));

        const featureImportance =
            shipmentData.sustainability_analysis.metrics;
        const radarData = Object.entries(featureImportance).map(([key, value]) => ({
            subject: key
                .split('_')
                .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
                .join(' '),
            importance: Number((Number(value)).toFixed(2)),
        }));

        const scores = [
            {
                name: `Shipment ${shipmentId}`,
                actual: Number(
                    shipmentData.sustainability_analysis.overall_sustainability_score.toFixed(2)
                ),
                predicted: Number(
                    shipmentData.sustainability_analysis.predictions.predicted_score.toFixed(2)
                ),
            },
        ];
        setSustainabilityScores(scores);

        const sustainabilityMetrics = results.map((result) => ({
            timestamp: new Date(result?.processed_data?.timestamp || Date.now()).toLocaleDateString(),
            carbon_footprint: result?.sustainability_analysis?.processed_data?.analytics?.sustainability_metrics?.carbon_footprint || 0,
            energy_efficiency: result?.sustainability_analysis?.processed_data?.analytics?.sustainability_metrics?.energy_efficiency || 0,
            resource_efficiency: result?.sustainability_analysis?.processed_data?.analytics?.sustainability_metrics?.resource_efficiency || 0,
            waste_reduction: result?.sustainability_analysis?.processed_data?.analytics?.sustainability_metrics?.waste_reduction || 0
        }));

        return {
            sustainabilityScores,
            sustainabilityMetrics,
            pieData,
            radarData,
        };
    };

    useEffect(() => {
        const chartData = processChartData(
            latestData,
            historyData,
            selectedShipmentId
        );
        setChartData(chartData);
    }, [latestData, historyData, selectedShipmentId]);

    const shipmentData = latestData?.results?.find(
        (result) => result.shipment_id === selectedShipmentId
    );

    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];
    const { theme } = useTheme();
    const scoreData = sustainabilityScores[0];
    const textColor = theme === 'dark' ? 'white' : 'black';
    return (

        <Sheet open={isOpen} onOpenChange={setIsOpen}>
            <SheetTrigger asChild>
                <Button
                    size="icon"
                    className={`${theme === 'dark' ? 'bg-black text-white' : 'bg-white text-black'}  hover:${theme === 'dark' ? 'bg-black' : 'bg-white'} hover:text-primary rounded-none fixed right-3 top-3 z-50 transition-colors duration-300`}
                    aria-label="Open Dashboard"
                >
                    <LayoutDashboard className="h-5 w-5" />
                </Button>
            </SheetTrigger>
            <SheetContent side="right" size="full" className={`p-0 border-none ${theme === 'dark' ? 'bg-black' : 'bg-white'}`}>
                <SheetHeader className="p-4 border-b">
                    <div className="flex items-center justify-between">
                        <SheetTitle className={`text-lg font-semibold ${theme === 'dark' ? 'text-white' : 'text-black'} `}>Analytics Dashboard</SheetTitle>
                        <Button
                            size="icon"
                            onClick={() => setIsOpen(false)}
                            className={`h-8 w-8 rounded-none ${theme === 'dark' ? 'bg-black text-white' : 'bg-white text-black'} hover:text-primary hover:${theme === 'dark' ? 'bg-black' : 'bg-white'} transition-colors duration-300`}
                        >
                            <X className="h-5 w-5" />
                        </Button>
                    </div>
                </SheetHeader>
                <ScrollArea className="h-[calc(100vh-100px)] p-4">
                    <div className="space-y-4">
                        <div>
                            <label className={`block ${theme === 'dark' ? 'text-white' : 'text-black'}  mb-2`}>Choose Shipment</label>
                            <ShipmentSelector
                                shipments={availableShipments}
                                selectedId={selectedShipmentId}
                                onSelect={setSelectedShipmentId}
                            />
                        </div>
                    </div>

                    {loading && (
                        <div className={`text-center ${theme === 'dark' ? 'text-white' : 'text-black'}  p-6`}>Loading...</div>
                    )}

                    {shipmentData?.llm_insights && (
                        <Card
                            className={`${theme === 'dark' ? 'bg-black text-white' : 'bg-white text-black'
                                } mb-4 mt-8 border-none rounded-none`}
                        >

                            <ScrollArea className="h-[300px] w-full rounded-none border p-4">
                                <h2 className="text-xl font-semibold mb-8">Sustainability Insights</h2>
                                <div className="pr-4">
                                    <ReactMarkdown
                                        className={`
                        prose
                        ${theme === 'dark' ? 'prose-invert' : ''}
                        max-w-none
                        prose-headings:font-semibold
                        prose-h1:text-xl
                        prose-h2:text-lg
                        prose-h3:text-md
                        prose-p:text-sm
                        prose-li:text-sm
                        prose-strong:text-primary
                        space-y-4
                    `}
                                    >
                                        {shipmentData.llm_insights}
                                    </ReactMarkdown>
                                </div>
                            </ScrollArea>
                        </Card>
                    )}

                    {selectedShipmentId && shipmentData && (

                        <div>
                            <ShippingKpiCards
                                shipmentId={selectedShipmentId}
                                transportMode={
                                    shipmentData.sustainability_analysis.processed_data.processed_data
                                        .transport_mode || 'N/A'
                                }
                                overallSustainabilityScore={
                                    shipmentData.sustainability_analysis.overall_sustainability_score ||
                                    0
                                }
                                materialType={
                                    (shipmentData.sustainability_analysis.processed_data.processed_data.packages as any[])[0].material_type
                                }
                            />
                        </div>
                    )}

                    {!loading && !error && chartData && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

                            {/* Metrics Overview */}
                            <ChartWrapper title="Metrics Distribution">
                                <ResponsiveContainer width="100%" height={400}>
                                    <PieChart>
                                        <Pie
                                            data={chartData.pieData}
                                            dataKey="value"
                                            nameKey="name"
                                            cx="50%"
                                            cy="50%"
                                            outerRadius={120}
                                            fill="#8884d8"
                                            label
                                        >
                                            {chartData.pieData.map((entry, index) => (
                                                <Cell
                                                    key={`cell-${index}`}
                                                    fill={COLORS[index % COLORS.length]}
                                                />
                                            ))}
                                        </Pie>
                                        <Tooltip
                                            contentStyle={{ backgroundColor: '#000' }}
                                            labelStyle={{ color: '#fff' }}
                                            itemStyle={{ color: '#fff' }} />
                                        <Legend />
                                    </PieChart>
                                </ResponsiveContainer>
                            </ChartWrapper>

                            {/* Feature Importance */}
                            <ChartWrapper title="Feature Importance">
                                <ResponsiveContainer width="100%" height={400}>
                                    <RadarChart data={chartData.radarData}>
                                        <PolarGrid />
                                        <PolarAngleAxis dataKey="subject" tick={{ fontSize: 12, fill: textColor }} />
                                        <PolarRadiusAxis angle={60} domain={[0, 100]} />
                                        <Radar
                                            name="Importance"
                                            dataKey="importance"
                                            stroke="#4caf50"
                                            fill="#4caf50"
                                            fillOpacity={0.8}
                                        />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: '#000' }}
                                            labelStyle={{ color: '#fff' }}
                                            itemStyle={{ color: '#fff' }} />
                                        <Legend />
                                    </RadarChart>
                                </ResponsiveContainer>
                            </ChartWrapper>

                            {/* Sustainability Scores */}
                            <ChartWrapper title="Sustainability Scores">
                                <div className="mt-14 flex flex-col md:flex-row md:justify-between">
                                    <Card
                                        className="w-full md:w-[48%] border-none shadow-none"
                                        style={{ backgroundColor: theme === 'dark' ? 'black' : 'white' }}
                                    >
                                        <CardHeader>
                                            <CardTitle className="text-center" style={{ color: textColor }}>
                                                Actual Score
                                            </CardTitle>
                                        </CardHeader>
                                        <CardContent>
                                            <ScoreDonutChart
                                                score={scoreData.actual}
                                                label="Actual Score"
                                                textColor={textColor}
                                            />
                                        </CardContent>
                                    </Card>
                                    <Card
                                        className="w-full md:w-[48%] border-none shadow-none mt-4 md:mt-0"
                                        style={{ backgroundColor: theme === 'dark' ? 'black' : 'white' }}
                                    >
                                        <CardHeader>
                                            <CardTitle className="text-center" style={{ color: textColor }}>
                                                Predicted Score
                                            </CardTitle>
                                        </CardHeader>
                                        <CardContent>
                                            <ScoreDonutChart
                                                score={scoreData.predicted}
                                                label="Predicted Score"
                                                textColor={textColor}
                                            />
                                        </CardContent>
                                    </Card>
                                </div>
                            </ChartWrapper>

                            {/* Sustainability Metrics */}
                            <ChartWrapper title="Sustainability Metrics">
                                <ResponsiveContainer width="100%" height={400}>
                                    <BarChart
                                        data={chartData.sustainabilityMetrics}
                                        margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                                    >
                                        <XAxis dataKey="timestamp" />
                                        <YAxis domain={[0, 100]} />
                                        <Tooltip
                                            contentStyle={{
                                                backgroundColor: theme === 'dark' ? '#000' : '#fff',
                                                border: '1px solid #ccc'
                                            }}
                                            labelStyle={{ color: theme === 'dark' ? '#fff' : '#000' }}
                                            itemStyle={{ color: theme === 'dark' ? '#fff' : '#000' }}
                                        />
                                        <Legend />
                                        <Bar
                                            dataKey="carbon_footprint"
                                            name="Carbon Footprint"
                                            fill="#8884d8"
                                            radius={[4, 4, 0, 0]}
                                        />
                                        <Bar
                                            dataKey="energy_efficiency"
                                            name="Energy Efficiency"
                                            fill="#82ca9d"
                                            radius={[4, 4, 0, 0]}
                                        />
                                        <Bar
                                            dataKey="resource_efficiency"
                                            name="Resource Efficiency"
                                            fill="#ffc658"
                                            radius={[4, 4, 0, 0]}
                                        />
                                        <Bar
                                            dataKey="waste_reduction"
                                            name="Waste Reduction"
                                            fill="#ff8042"
                                            radius={[4, 4, 0, 0]}
                                        />
                                    </BarChart>
                                </ResponsiveContainer>
                            </ChartWrapper>
                        </div>
                    )}

                    {!loading && !error && !chartData && (
                        <div className={`text-center ${theme === 'dark' ? 'text-white' : 'text-black'}  py-6`}>
                            No Data Available
                        </div>
                    )}
                </ScrollArea>
            </SheetContent>
        </Sheet>
    );
};

export default Dashboard;