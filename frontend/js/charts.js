// D3.js Chart for Balance Forecast
function createBalanceForecastChart(data) {
    // Clear existing chart
    d3.select('#balanceChart').selectAll('*').remove();

    if (!data.dates || data.dates.length === 0) {
        d3.select('#balanceChart')
            .append('p')
            .style('text-align', 'center')
            .style('color', '#94a3b8')
            .text('Upload transactions to see forecast');
        return;
    }

    // Set dimensions
    const margin = { top: 20, right: 30, bottom: 40, left: 60 };
    const container = document.getElementById('balanceChart');
    const width = container.offsetWidth - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;

    // Create SVG
    const svg = d3.select('#balanceChart')
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    // Parse data
    const chartData = data.dates.map((date, i) => ({
        date: new Date(date),
        balance: data.predicted_balance[i]
    }));

    // Scales
    const xScale = d3.scaleTime()
        .domain(d3.extent(chartData, d => d.date))
        .range([0, width]);

    const yScale = d3.scaleLinear()
        .domain([
            Math.min(0, d3.min(chartData, d => d.balance) * 1.1),
            d3.max(chartData, d => d.balance) * 1.1
        ])
        .range([height, 0]);

    // Create gradient
    const gradient = svg.append('defs')
        .append('linearGradient')
        .attr('id', 'balance-gradient')
        .attr('gradientUnits', 'userSpaceOnUse')
        .attr('x1', 0)
        .attr('y1', yScale(d3.max(chartData, d => d.balance)))
        .attr('x2', 0)
        .attr('y2', yScale(d3.min(chartData, d => d.balance)));

    gradient.append('stop')
        .attr('offset', '0%')
        .attr('stop-color', '#10b981');

    gradient.append('stop')
        .attr('offset', '100%')
        .attr('stop-color', '#ef4444');

    // Line generator
    const line = d3.line()
        .x(d => xScale(d.date))
        .y(d => yScale(d.balance))
        .curve(d3.curveMonotoneX);

    // Area generator
    const area = d3.area()
        .x(d => xScale(d.date))
        .y0(height)
        .y1(d => yScale(d.balance))
        .curve(d3.curveMonotoneX);

    // Add area
    svg.append('path')
        .datum(chartData)
        .attr('fill', 'url(#balance-gradient)')
        .attr('opacity', 0.2)
        .attr('d', area);

    // Add line
    svg.append('path')
        .datum(chartData)
        .attr('fill', 'none')
        .attr('stroke', 'url(#balance-gradient)')
        .attr('stroke-width', 3)
        .attr('d', line);

    // Add zero line
    svg.append('line')
        .attr('x1', 0)
        .attr('x2', width)
        .attr('y1', yScale(0))
        .attr('y2', yScale(0))
        .attr('stroke', '#94a3b8')
        .attr('stroke-dasharray', '5,5')
        .attr('opacity', 0.5);

    // Add dots
    svg.selectAll('.dot')
        .data(chartData)
        .enter()
        .append('circle')
        .attr('class', 'dot')
        .attr('cx', d => xScale(d.date))
        .attr('cy', d => yScale(d.balance))
        .attr('r', 4)
        .attr('fill', d => d.balance >= 0 ? '#10b981' : '#ef4444')
        .attr('stroke', '#0f172a')
        .attr('stroke-width', 2)
        .on('mouseover', function (event, d) {
            d3.select(this).attr('r', 6);

            // Show tooltip
            const tooltip = svg.append('g')
                .attr('class', 'tooltip')
                .attr('transform', `translate(${xScale(d.date)},${yScale(d.balance) - 30})`);

            tooltip.append('rect')
                .attr('x', -50)
                .attr('y', -20)
                .attr('width', 100)
                .attr('height', 25)
                .attr('fill', '#1e293b')
                .attr('stroke', '#334155')
                .attr('rx', 5);

            tooltip.append('text')
                .attr('text-anchor', 'middle')
                .attr('y', -5)
                .attr('fill', '#f1f5f9')
                .attr('font-size', '12px')
                .text(`₹${d.balance.toLocaleString('en-IN')}`);
        })
        .on('mouseout', function () {
            d3.select(this).attr('r', 4);
            svg.selectAll('.tooltip').remove();
        });

    // X Axis
    const xAxis = d3.axisBottom(xScale)
        .ticks(6)
        .tickFormat(d3.timeFormat('%b %d'));

    svg.append('g')
        .attr('transform', `translate(0,${height})`)
        .call(xAxis)
        .attr('color', '#94a3b8');

    // Y Axis
    const yAxis = d3.axisLeft(yScale)
        .ticks(5)
        .tickFormat(d => `₹${(d / 1000).toFixed(0)}k`);

    svg.append('g')
        .call(yAxis)
        .attr('color', '#94a3b8');

    // Highlight low balance dates
    if (data.low_balance_dates && data.low_balance_dates.length > 0) {
        data.low_balance_dates.forEach(dateStr => {
            const date = new Date(dateStr);
            const dataPoint = chartData.find(d =>
                d.date.toDateString() === date.toDateString()
            );

            if (dataPoint) {
                svg.append('circle')
                    .attr('cx', xScale(dataPoint.date))
                    .attr('cy', yScale(dataPoint.balance))
                    .attr('r', 8)
                    .attr('fill', 'none')
                    .attr('stroke', '#f59e0b')
                    .attr('stroke-width', 2)
                    .attr('opacity', 0.7);
            }
        });
    }
}
