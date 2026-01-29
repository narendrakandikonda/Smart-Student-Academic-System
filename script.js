let marksData = {};

// Show custom notification
function showNotification(message, type = 'success') {
  const notification = document.createElement('div');
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 15px 25px;
    background: ${type === 'success' ? '#27ae60' : '#e74c3c'};
    color: white;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    font-weight: 600;
    animation: slideIn 0.3s ease-in-out;
    z-index: 1000;
  `;
  notification.textContent = message;
  document.body.appendChild(notification);
  setTimeout(() => notification.remove(), 3000);
}

function addStudent() {
  const rollVal = document.getElementById("roll").value.trim();
  const nameVal = document.getElementById("name").value.trim();

  if (!rollVal || !nameVal) {
    showNotification("Please enter both Roll No and Name", 'error');
    return;
  }

  fetch("http://127.0.0.1:5000/add_student", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      roll: rollVal,
      name: nameVal
    })
  })
    .then(res => res.json())
    .then(data => {
      showNotification(data.msg, 'success');
      document.getElementById("roll").value = '';
      document.getElementById("name").value = '';
    })
    .catch(err => showNotification("Error: " + err, 'error'));
}

function addSubject() {
  const r = document.getElementById("marksRoll").value.trim();
  const sub = document.getElementById("subject").value.trim();
  const m = document.getElementById("mark").value.trim();

  if (!r || !sub || !m) {
    showNotification("Please fill all fields", 'error');
    return;
  }

  if (isNaN(m) || m < 0 || m > 100) {
    showNotification("Marks must be between 0-100", 'error');
    return;
  }

  if (!marksData[r]) marksData[r] = {};
  marksData[r][sub] = parseInt(m);
  showNotification(`${sub}: ${m} marks added for Roll ${r}`, 'success');
  document.getElementById("subject").value = '';
  document.getElementById("mark").value = '';
}

function submitMarks() {
  const r = document.getElementById("marksRoll").value.trim();

  if (!r || !marksData[r] || Object.keys(marksData[r]).length === 0) {
    showNotification("Add subjects first", 'error');
    return;
  }

  fetch('http://127.0.0.1:5000/add_marks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ roll: r, marks: marksData[r] })
  })
    .then(r => r.json())
    .then(d => {
      showNotification(d.msg, 'success');
      delete marksData[r];
      document.getElementById("marksRoll").value = '';
    })
    .catch(err => showNotification("Error: " + err, 'error'));
}

function updateMarks() {
  const roll = document.getElementById("editRoll").value.trim();
  const subject = document.getElementById("editSubject").value.trim();
  const mark = document.getElementById("editMark").value.trim();

  if (!roll || !subject || !mark) {
    showNotification("Please fill all fields", 'error');
    return;
  }

  if (isNaN(mark) || mark < 0 || mark > 100) {
    showNotification("Marks must be between 0-100", 'error');
    return;
  }

  fetch('http://127.0.0.1:5000/update_marks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      roll: roll, 
      subject: subject,
      marks: parseInt(mark)
    })
  })
    .then(res => res.json())
    .then(data => {
      showNotification(data.msg, 'success');
      document.getElementById("editRoll").value = '';
      document.getElementById("editSubject").value = '';
      document.getElementById("editMark").value = '';
    })
    .catch(err => showNotification("Error: " + err, 'error'));
}

function markAttendance(status) {
  const roll = document.getElementById("attRoll").value.trim();

  if (!roll) {
    showNotification("Please enter Roll Number", 'error');
    return;
  }

  // Get today's date
  const today = new Date();
  const dateStr = today.toISOString().split('T')[0];
  const formattedDate = today.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });

  fetch('http://127.0.0.1:5000/mark_attendance', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ roll: roll, status, date: dateStr })
  })
    .then(r => r.json())
    .then(d => {
      showNotification(`${status} marked for ${formattedDate}`, 'success');
      document.getElementById("attRoll").value = '';
    })
    .catch(err => showNotification("Error: " + err, 'error'));
}

function undoAttendance() {
  fetch('http://127.0.0.1:5000/undo_attendance', {
    method: 'POST'
  })
    .then(r => r.json())
    .then(d => showNotification(`Undone: ${JSON.stringify(d.undone)}`, 'success'))
    .catch(err => showNotification("Error: " + err, 'error'));
}

// Format student data into attractive display
function formatStudentData(data) {
  if (Array.isArray(data)) {
    return data.map(student => formatStudentCard(student)).join('');
  }
  return formatStudentCard(data);
}

function formatStudentCard(student) {
  if (!student || !student.name) return '';

  const gradeColor = getGradeColor(student.grade);
  const totalMarksPerSubject = 80;
  const marksHtml = student.marks ? Object.entries(student.marks)
    .map(([subject, mark]) => `<div class="mark-item"><span class="subject">${subject}</span><span class="mark-value">${mark}/${totalMarksPerSubject}</span></div>`)
    .join('') : '';

  const latestAttendance = student.attendance && student.attendance.length > 0 ? student.attendance[student.attendance.length - 1] : null;
  const attendanceStatus = latestAttendance ? latestAttendance.status : 'N/A';
  const attendanceDate = latestAttendance ? latestAttendance.date : '';
  const attendanceColor = attendanceStatus === 'Present' ? '#27ae60' : '#e74c3c';

  // Build attendance history HTML
  const attendanceHistoryHtml = student.attendance && student.attendance.length > 0 ? `
    <div class="attendance-history">
      <h4>Recent Attendance Records</h4>
      <div class="attendance-list">
        ${student.attendance.slice().reverse().slice(0, 10).map((record, idx) => {
          const dateObj = new Date(record.date + 'T00:00:00');
          const formattedDate = dateObj.toLocaleDateString('en-US', { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' });
          const statusColor = record.status === 'Present' ? '#27ae60' : '#e74c3c';
          return `<div class="attendance-record" style="display: flex; justify-content: space-between; padding: 8px; background: #f5f5f5; margin: 4px 0; border-radius: 4px;">
            <span>${formattedDate}</span>
            <span style="background: ${statusColor}; color: white; padding: 2px 10px; border-radius: 3px; font-weight: 600;">${record.status}</span>
          </div>`;
        }).join('')}
      </div>
    </div>
  ` : '';

  return `
    <div class="student-card">
      <div class="student-header">
        <h3>${student.name}</h3>
        <span class="roll-badge">${student.roll}</span>
      </div>
      
      <div class="student-body">
        <div class="info-grid">
          <div class="info-item">
            <label>Grade</label>
            <span class="grade-badge" style="background: ${gradeColor}">${student.grade || 'N/A'}</span>
          </div>
          <div class="info-item">
            <label>Percentage</label>
            <span class="percentage">${student.percentage ? student.percentage.toFixed(2) : 0}%</span>
          </div>
          <div class="info-item">
            <label>Total Marks</label>
            <span class="total-marks">${student.total || 0}/${student.max_marks || 500}</span>
          </div>
          <div class="info-item">
            <label>Latest Attendance</label>
            <span class="attendance-badge" style="background: ${attendanceColor}">${attendanceStatus}${attendanceDate ? ' (' + new Date(attendanceDate + 'T00:00:00').toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) + ')' : ''}</span>
          </div>
        </div>

        ${marksHtml ? `
          <div class="marks-section">
            <h4>Subject-wise Marks</h4>
            <div class="marks-grid">
              ${marksHtml}
            </div>
          </div>
        ` : ''}

        ${attendanceHistoryHtml}

        ${student.calendar ? `
          <div class="marks-section">
            <h4>Attendance Calendar — ${student.attendance_period.month}/${student.attendance_period.year}</h4>
            <div id="calendar-${student.roll}" class="calendar-root"></div>
            <div style="margin-top:8px;display:flex;gap:12px;align-items:center;">
              <div><strong>Month Present:</strong> ${student.attendance_period_summary.present_days}/${student.attendance_period_summary.total_days}</div>
              <div><strong>Percentage:</strong> ${student.attendance_period_summary.percentage.toFixed(2)}%</div>
            </div>
          </div>
        ` : ''}
      </div>
    </div>
  `;
}

// render calendar into container element given student.calendar and meta
function renderCalendar(student) {
  if (!student || !student.calendar) return;
  const container = document.getElementById(`calendar-${student.roll}`);
  if (!container) return;
  container.innerHTML = buildCalendarHtml(student.calendar, student.calendar_meta);
}

function buildCalendarHtml(calendarArr, meta) {
  // meta.month_start_weekday: 0=Monday
  const daysOfWeek = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
  const ndays = calendarArr.length;
  const startWeekday = meta && meta.month_start_weekday != null ? meta.month_start_weekday : (new Date(calendarArr[0].date)).getDay();

  // build table
  let html = `<table class="calendar-table"><thead><tr>`;
  for (let d of daysOfWeek) html += `<th>${d}</th>`;
  html += `</tr></thead><tbody>`;

  let day = 0;
  // monthrange: startWeekday is 0=Monday; JS getDay() uses 0=Sunday so adjust if needed
  let firstCol = startWeekday; // 0..6 where 0=Monday
  // convert firstCol to table column where Mon=0..Sun=6
  for (let r=0; r<6 && day < ndays; r++) {
    html += '<tr>';
    for (let c=0; c<7; c++) {
      if (r===0 && c < firstCol) {
        html += '<td class="calendar-cell empty"></td>';
      } else if (day < ndays) {
        const item = calendarArr[day++];
        const s = item.status ? String(item.status).toLowerCase() : '';
        let cls = 'calendar-cell';
        if (s === 'p' || s === 'present' || s === 'true' || s === '1' || s === 'yes') cls += ' present';
        else if (s) cls += ' absent';
        html += `<td class="${cls}"><div class="cell-day">${item.day}</div>${item.status ? `<div class="cell-status">${item.status}</div>` : ''}</td>`;
      } else {
        html += '<td class="calendar-cell empty"></td>';
      }
    }
    html += '</tr>';
  }

  html += '</tbody></table>';
  return html;
}

function getGradeColor(grade) {
  const gradeColors = {
    'A': '#27ae60',
    'B': '#3498db',
    'C': '#f39c12',
    'D': '#e67e22',
    'F': '#e74c3c'
  };
  return gradeColors[grade] || '#95a5a6';
}

function loadStudents() {
  fetch('http://127.0.0.1:5000/students')
    .then(r => r.json())
    .then(d => {
      const output = document.getElementById('output');
      output.innerHTML = formatStudentData(d);
      showNotification('Students loaded successfully', 'success');
    })
    .catch(err => showNotification("Error loading students", 'error'));
}

function getStudent() {
  const roll = document.getElementById("searchRoll").value.trim();
  const month = document.getElementById("searchMonth").value.trim();
  const year = document.getElementById("searchYear").value.trim();

  if (!roll) {
    showNotification("Enter Roll Number", 'error');
    return;
  }

  let url = `http://127.0.0.1:5000/student/${roll}`;
  const params = [];
  if (month) params.push(`month=${encodeURIComponent(month)}`);
  if (year) params.push(`year=${encodeURIComponent(year)}`);
  if (params.length) url += `?${params.join('&')}`;

  fetch(url)
    .then(res => res.json())
    .then(data => {
      const output = document.getElementById('output');
      if (data.error) {
        showNotification(data.error, 'error');
      } else {
        output.innerHTML = formatStudentData(data);
        // render calendar if present
        if (Array.isArray(data)) data.forEach(d => renderCalendar(d));
        else renderCalendar(data);
        showNotification('Student found', 'success');
      }
    })
    .catch(err => showNotification("Error fetching student", 'error'));
}

function getSemesterAttendance() {
  const roll = document.getElementById("semesterRoll").value.trim();
  const months = document.getElementById("semesterMonths").value.trim() || '6';

  if (!roll) {
    showNotification("Enter Roll Number", 'error');
    return;
  }

  fetch(`http://127.0.0.1:5000/semester_attendance/${roll}?months=${encodeURIComponent(months)}`)
    .then(res => res.json())
    .then(data => {
      const container = document.getElementById('semester-report-container');
      if (data.error) {
        showNotification(data.error, 'error');
        container.innerHTML = '';
      } else {
        const attendanceColor = data.semester_attendance_percentage >= 75 ? '#27ae60' : data.semester_attendance_percentage >= 60 ? '#f39c12' : '#e74c3c';
        container.innerHTML = `
          <div style="background: linear-gradient(135deg, ${attendanceColor}20 0%, ${attendanceColor}10 100%); border-left: 4px solid ${attendanceColor}; padding: 16px; border-radius: 8px;">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
              <div>
                <label style="font-size: 12px; color: #666; font-weight: 600;">Student Name</label>
                <p style="margin: 8px 0; font-size: 18px; font-weight: 600;">${data.name}</p>
              </div>
              <div>
                <label style="font-size: 12px; color: #666; font-weight: 600;">Roll Number</label>
                <p style="margin: 8px 0; font-size: 18px; font-weight: 600;">${data.roll}</p>
              </div>
              <div>
                <label style="font-size: 12px; color: #666; font-weight: 600;">Semester Duration</label>
                <p style="margin: 8px 0; font-size: 16px;">${data.semester_months} months</p>
              </div>
              <div>
                <label style="font-size: 12px; color: #666; font-weight: 600;">Days Present</label>
                <p style="margin: 8px 0; font-size: 16px;">${data.present_days}/${data.total_working_days}</p>
              </div>
              <div style="grid-column: 1 / -1;">
                <label style="font-size: 12px; color: #666; font-weight: 600;">Semester Attendance Percentage</label>
                <div style="margin: 8px 0; font-size: 28px; font-weight: 700; color: ${attendanceColor};">
                  ${data.semester_attendance_percentage.toFixed(2)}%
                </div>
                <div style="margin-top: 8px; width: 100%; height: 10px; background: #ddd; border-radius: 5px; overflow: hidden;">
                  <div style="width: ${data.semester_attendance_percentage}%; height: 100%; background: ${attendanceColor}; transition: width 0.3s ease;"></div>
                </div>
              </div>
            </div>
          </div>
        `;
        showNotification('Semester attendance report loaded', 'success');
      }
    })
    .catch(err => showNotification("Error fetching semester attendance", 'error'));
}

