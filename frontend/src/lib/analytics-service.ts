import { supabase } from '@/lib/supabase';

interface Prediction {
  predicted_score: number;
  feature_importances: {
    [key: string]: number;
  };
  alternative_modes: string[];
  estimated_savings: number;
}

interface Metrics {
  package_sustainability_index: number;
  route_efficiency_score: number;
  carbon_emission_index: number;
  resource_utilization_rate: number;
  energy_efficiency_rating: number;
  waste_reduction_score: number;
  carbon_emissions: number;
  distance: number;
  transport_mode: string;
  [key: string]: number | string;
}

export interface SustainabilityAnalytics {
    results: any;
    timestamp: string;
    num_shipments_analyzed: number;
    summary_statistics: any;
    detailed_results: DetailedResult[];
  }
  
  interface DetailedResult {
    shipment_id: string;
    metrics: Metrics;
    overall_sustainability_score: number;
    predictions: Prediction;
  }

  export async function storeAnalyticsData(data: SustainabilityAnalytics) {
    try {
      const userId = (await supabase.auth.getUser()).data?.user?.id;
      if (!userId) throw new Error('User not authenticated');
  
      const { data: analyticsData, error: analyticsError } = await supabase
        .from('sustainability_analytics')
        .insert([
          {
            timestamp: data.timestamp,
            data: data,
            num_shipments: data.num_shipments_analyzed,
            user_id: userId,
          },
        ])
        .select()
        .single();
  
      if (analyticsError) throw analyticsError;
      return analyticsData;
    } catch (error) {
      console.error('Error storing analytics data:', error);
      throw error;
    }
  }
  
  export async function getLatestAnalytics() {
    try {
      const userId = (await supabase.auth.getUser()).data?.user?.id;
      if (!userId) throw new Error('User not authenticated');
  
      const { data, error } = await supabase
        .from('sustainability_analytics')
        .select('*')
        .order('timestamp', { ascending: false })
        .eq('user_id', userId)
        .limit(1)
        .single();
  
      if (error) throw error;
      return data?.data as SustainabilityAnalytics;
    } catch (error) {
      console.error('Error fetching latest analytics:', error);
      throw error;
    }
  }
  
  export async function getAnalyticsHistory(limit: number = 10) {
    try {
      const userId = (await supabase.auth.getUser()).data?.user?.id;
      if (!userId) throw new Error('User not authenticated');
  
      const { data, error } = await supabase
        .from('sustainability_analytics')
        .select('*')
        .order('timestamp', { ascending: false })
        .eq('user_id', userId)
        .limit(limit);
  
      if (error) throw error;
      return data.map((record) => record.data) as SustainabilityAnalytics[];
    } catch (error) {
      console.error('Error fetching analytics history:', error);
      throw error;
    }
  }