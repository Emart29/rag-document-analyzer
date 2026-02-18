import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import { Badge } from './ui/Badge';
import { observabilityAPI } from '../services/api';

const currency = (value) => `$${Number(value || 0).toFixed(6)}`;

export default function ObservabilityDashboard() {
  const { data: metricsData } = useQuery({
    queryKey: ['observability-metrics'],
    queryFn: async () => {
      const res = await observabilityAPI.getMetrics(168);
      return res.data;
    },
    refetchInterval: 30000,
  });

  const { data: logsData } = useQuery({
    queryKey: ['observability-logs'],
    queryFn: async () => {
      const res = await observabilityAPI.getLogs(20);
      return res.data;
    },
    refetchInterval: 30000,
  });

  const { data: promptsData } = useQuery({
    queryKey: ['observability-prompts'],
    queryFn: async () => {
      const res = await observabilityAPI.getPrompts();
      return res.data;
    },
  });

  const summary = metricsData?.summary || {};
  const trends = metricsData?.trends || [];
  const recentLogs = logsData || [];
  const prompts = promptsData || [];

  const activePrompts = useMemo(
    () => prompts.filter((item) => item.is_active),
    [prompts]
  );

  return (
    <div className="p-6 overflow-y-auto h-full space-y-6">
      <h2 className="text-2xl font-bold">LLM Observability Dashboard</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        <MetricCard title="Total Queries" value={summary.total_queries || 0} />
        <MetricCard title="Total Tokens" value={summary.total_tokens || 0} />
        <MetricCard title="Total Cost" value={currency(summary.total_cost_usd)} />
        <MetricCard title="Avg Latency" value={`${Number(summary.average_latency_ms || 0).toFixed(2)} ms`} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Daily Usage Trend</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {trends.length === 0 && <p className="text-sm text-muted-foreground">No trend data yet.</p>}
              {trends.map((row) => (
                <div key={row.date} className="border rounded p-3">
                  <div className="font-medium">{row.date}</div>
                  <div className="text-sm text-muted-foreground">
                    Queries: {row.queries} • Tokens: {row.tokens} • Cost: {currency(row.cost_usd)} • Avg Latency: {row.average_latency_ms} ms
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Prompt Templates</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {activePrompts.map((prompt) => (
                <div key={prompt.id} className="border rounded p-3">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{prompt.template_key} v{prompt.version}</span>
                    <Badge>active</Badge>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">{prompt.description || 'No description provided.'}</p>
                </div>
              ))}
              {activePrompts.length === 0 && <p className="text-sm text-muted-foreground">No prompt templates found.</p>}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent LLM Calls</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left border-b">
                  <th className="py-2">Time</th>
                  <th className="py-2">Question</th>
                  <th className="py-2">Tokens</th>
                  <th className="py-2">Cost</th>
                  <th className="py-2">Latency</th>
                  <th className="py-2">Status</th>
                </tr>
              </thead>
              <tbody>
                {recentLogs.map((log) => (
                  <tr key={log.id} className="border-b last:border-0">
                    <td className="py-2 pr-2">{new Date(log.created_at).toLocaleString()}</td>
                    <td className="py-2 pr-2 max-w-[360px] truncate">{log.question || '-'}</td>
                    <td className="py-2 pr-2">{log.total_tokens}</td>
                    <td className="py-2 pr-2">{currency(log.cost_usd)}</td>
                    <td className="py-2 pr-2">{Number(log.latency_ms).toFixed(2)} ms</td>
                    <td className="py-2">
                      <Badge variant={log.success ? 'default' : 'destructive'}>{log.success ? 'success' : 'failure'}</Badge>
                    </td>
                  </tr>
                ))}
                {recentLogs.length === 0 && (
                  <tr>
                    <td colSpan={6} className="py-4 text-center text-muted-foreground">No logs yet.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function MetricCard({ title, value }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm text-muted-foreground">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-2xl font-semibold">{value}</p>
      </CardContent>
    </Card>
  );
}
