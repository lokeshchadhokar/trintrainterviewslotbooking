document.addEventListener('DOMContentLoaded', function () {
    const mentorSelect = document.getElementById('mentor');
    const dateSelect = document.getElementById('date');
    const timeSelect = document.getElementById('time');

    function updateAvailableSlots() {
        const selectedMentor = mentorSelect.value;
        const selectedDate = dateSelect.value;
        
        if (selectedMentor && selectedDate) {
            fetch(`/available_slots?mentor=${selectedMentor}&date=${selectedDate}`)
                .then(response => response.json())
                .then(data => {
                    timeSelect.innerHTML = '<option value="">-- Select a Time Slot --</option>';
                    data.available_slots.forEach(slot => {
                        const option = document.createElement('option');
                        option.value = slot;
                        option.textContent = slot;
                        timeSelect.appendChild(option);
                    });
                })
                .catch(error => console.error('Error fetching available slots:', error));
        }
    }

    mentorSelect.addEventListener('change', updateAvailableSlots);
    dateSelect.addEventListener('change', updateAvailableSlots);

    document.getElementById('round').addEventListener('change', function() {
        const roundSelected = this.value;
        const mentor = document.getElementById('mentor').value;
        const date = document.getElementById('date').value;
        
        fetch('/available_slots', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mentor, date, round: roundSelected })
        })
        .then(response => response.json())
        .then(slots => {
            const timeSlotSelect = document.getElementById('time');
            timeSlotSelect.innerHTML = ''; // Clear previous options
            slots.available_slots.forEach(slot => {
                const option = document.createElement('option');
                option.value = slot;
                option.text = slot;
                timeSlotSelect.add(option);
            });
        });
    });
});
