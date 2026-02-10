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
    const margin = { top: 30, right: 40, bottom: 80, left: 80 }; // Increased bottom and left margins
    const container = document.getElementById('balanceChart');
    const width = container.getBoundingClientRect().width - margin.left - margin.right;
    const height = 450 - margin.top - margin.bottom;

    // Create SVG
    const svg = d3.select('#balanceChart')
        .append('svg')
        .attr('viewBox', `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
        .attr('preserveAspectRatio', 'xMidYMid meet') // Use xMidYMid for better centering
        .attr('width', '100%')
        .attr('height', '100%')
        .style('max-height', '450px')
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
        .attr('x1', '0%').attr('y1', '0%')
        .attr('x2', '0%').attr('y2', '100%');

    gradient.append('stop')
        .attr('offset', '0%')
        .attr('stop-color', '#10b981')
        .attr('stop-opacity', 0.8);

    gradient.append('stop')
        .attr('offset', '100%')
        .attr('stop-color', '#ef4444')
        .attr('stop-opacity', 0.8);

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
        .attr('opacity', 0.1)
        .attr('d', area);

    // Add line
    svg.append('path')
        .datum(chartData)
        .attr('fill', 'none')
        .attr('stroke', 'var(--primary)')
        .attr('stroke-width', 2)
        .attr('d', line);

    // Add zero line
    svg.append('line')
        .attr('x1', 0)
        .attr('x2', width)
        .attr('y1', yScale(0))
        .attr('y2', yScale(0))
        .attr('stroke', '#475569')
        .attr('stroke-dasharray', '4,4')
        .attr('opacity', 0.5);

    // Tooltip overlay
    const focus = svg.append('g')
        .style('display', 'none');

    focus.append('line')
        .attr('class', 'x-hover-line hover-line')
        .attr('y1', 0)
        .attr('y2', height)
        .attr('stroke', '#6366f1')
        .attr('stroke-width', 1)
        .attr('stroke-dasharray', '3,3');

    focus.append('circle')
        .attr('r', 5)
        .attr('fill', '#6366f1')
        .attr('stroke', '#fff')
        .attr('stroke-width', 2);

    const tooltip = d3.select('body').append('div')
        .attr('class', 'chart-tooltip')
        .style('position', 'absolute')
        .style('padding', '8px 12px')
        .style('background', 'rgba(30, 41, 59, 0.95)')
        .style('border', '1px solid #334155')
        .style('border-radius', '6px')
        .style('color', '#fff')
        .style('font-size', '12px')
        .style('pointer-events', 'none')
        .style('display', 'none');

    svg.append('rect')
        .attr('width', width)
        .attr('height', height)
        .style('fill', 'none')
        .style('pointer-events', 'all')
        .on('mouseover', () => { focus.style('display', null); tooltip.style('display', 'block'); })
        .on('mouseout', () => { focus.style('display', 'none'); tooltip.style('display', 'none'); })
        .on('mousemove', function (event) {
            const bisectDate = d3.bisector(d => d.date).left;
            const x0 = xScale.invert(d3.pointer(event)[0]);
            const i = bisectDate(chartData, x0, 1);
            const d0 = chartData[i - 1];
            const d1 = chartData[i];
            const d = x0 - d0.date > d1.date - x0 ? d1 : d0;

            focus.attr('transform', `translate(${xScale(d.date)},${yScale(d.balance)})`);
            focus.select('.x-hover-line').attr('y2', height - yScale(d.balance));

            tooltip
                .html(`<strong>${d3.timeFormat('%b %d, %Y')(d.date)}</strong><br/>Balance: ₹${d.balance.toLocaleString('en-IN')}`)
                .style('left', (event.pageX + 15) + 'px')
                .style('top', (event.pageY - 40) + 'px');
        });

    // X Axis
    const xAxis = d3.axisBottom(xScale)
        .ticks(Math.max(width / 100, 4))
        .tickFormat(d3.timeFormat('%b %Y'));

    svg.append('g')
        .attr('transform', `translate(0,${height})`)
        .call(xAxis)
        .attr('color', '#94a3b8')
        .selectAll('text')
        .style('text-anchor', 'end')
        .attr('dx', '-.8em')
        .attr('dy', '.15em')
        .attr('transform', 'rotate(-35)');

    // Y Axis
    const yAxis = d3.axisLeft(yScale)
        .ticks(6)
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
