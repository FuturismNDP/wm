import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Circle
import math

class PivotVisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Pivot Visualizer")
        self.root.geometry("1000x700")
        
        # Khởi tạo dữ liệu
        self.raw_data = {}
        self.pivot_data = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame chính
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame cho input data
        input_frame = ttk.LabelFrame(main_frame, text="Dữ liệu đầu vào", padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Tạo 4 ô input cho 4 cột
        self.create_input_fields(input_frame)
        
        # Frame cho filter và buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Filter cho md_position
        filter_frame = ttk.LabelFrame(control_frame, text="Filter md_position", padding=5)
        filter_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        self.filter_var = tk.StringVar()
        self.filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, 
                                        state="readonly", width=15)
        self.filter_combo.pack()
        self.filter_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.LEFT)
        
        ttk.Button(button_frame, text="Tạo Pivot", command=self.create_pivot).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Vẽ đường tròn", command=self.draw_circle).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Xóa dữ liệu", command=self.clear_data).pack(side=tk.LEFT, padx=5)
        
        # Frame cho kết quả
        result_frame = ttk.Frame(main_frame)
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview để hiển thị pivot table
        self.setup_treeview(result_frame)
        
        # Canvas cho matplotlib
        self.setup_matplotlib(result_frame)
        
    def create_input_fields(self, parent):
        # Frame cho labels
        label_frame = ttk.Frame(parent)
        label_frame.pack(fill=tk.X, pady=(0, 5))
        
        labels = ["x_Rows", "y_Columns", "CA_1", "md_position"]
        for i, label in enumerate(labels):
            ttk.Label(label_frame, text=label, width=15).grid(row=0, column=i, padx=5)
        
        # Frame cho text widgets
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text_widgets = []
        for i in range(4):
            text_widget = tk.Text(text_frame, height=8, width=15)
            text_widget.grid(row=0, column=i, padx=5, sticky="nsew")
            self.text_widgets.append(text_widget)
            
        # Configure grid weights
        for i in range(4):
            text_frame.columnconfigure(i, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
    def setup_treeview(self, parent):
        # Frame cho treeview
        tree_frame = ttk.LabelFrame(parent, text="Pivot Table", padding=5)
        tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Treeview với scrollbars
        tree_container = ttk.Frame(tree_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(tree_container)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars và treeview
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_matplotlib(self, parent):
        # Frame cho matplotlib
        plot_frame = ttk.LabelFrame(parent, text="Visualization", padding=5)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Tạo figure
        self.fig, self.ax = plt.subplots(figsize=(6, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def parse_input_data(self):
        try:
            # Lấy dữ liệu từ 4 text widgets
            columns_data = []
            column_names = ["x_Rows", "y_Columns", "CA_1", "md_position"]
            
            for i, text_widget in enumerate(self.text_widgets):
                data = text_widget.get("1.0", tk.END).strip()
                if not data:
                    messagebox.showerror("Lỗi", f"Vui lòng nhập dữ liệu cho cột {column_names[i]}")
                    return False
                
                # Tách dữ liệu theo dòng
                lines = [line.strip() for line in data.split('\n') if line.strip()]
                columns_data.append(lines)
            
            # Kiểm tra độ dài các cột
            lengths = [len(col) for col in columns_data]
            if len(set(lengths)) > 1:
                messagebox.showerror("Lỗi", "Các cột phải có cùng số lượng dòng dữ liệu")
                return False
            
            # Lưu dữ liệu
            self.raw_data = {}
            for i, col_name in enumerate(column_names):
                if col_name == "CA_1":
                    # Chuyển đổi CA_1 thành số
                    try:
                        self.raw_data[col_name] = [float(x) for x in columns_data[i]]
                    except ValueError:
                        messagebox.showerror("Lỗi", "Cột CA_1 phải chứa các giá trị số")
                        return False
                else:
                    self.raw_data[col_name] = columns_data[i]
            
            # Cập nhật filter combo
            unique_positions = sorted(list(set(self.raw_data['md_position'])))
            self.filter_combo['values'] = ['Tất cả'] + unique_positions
            self.filter_combo.set('Tất cả')
            
            return True
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi khi xử lý dữ liệu: {str(e)}")
            return False
    
    def get_filtered_data(self):
        if not self.raw_data:
            return {}
        
        filter_value = self.filter_var.get()
        if filter_value == 'Tất cả' or filter_value == '':
            return self.raw_data
        
        # Lọc dữ liệu
        filtered_data = {key: [] for key in self.raw_data.keys()}
        for i, pos in enumerate(self.raw_data['md_position']):
            if pos == filter_value:
                for key in self.raw_data.keys():
                    filtered_data[key].append(self.raw_data[key][i])
        
        return filtered_data
    
    def create_pivot_table(self, data):
        # Tạo pivot table thủ công
        pivot = {}
        
        # Lấy unique values
        x_values = sorted(list(set(data['x_Rows'])))
        y_values = sorted(list(set(data['y_Columns'])))
        
        # Khởi tạo pivot table
        for x in x_values:
            pivot[x] = {}
            for y in y_values:
                pivot[x][y] = 0
        
        # Tính tổng
        for i in range(len(data['x_Rows'])):
            x = data['x_Rows'][i]
            y = data['y_Columns'][i]
            value = data['CA_1'][i]
            pivot[x][y] += value
        
        return pivot, x_values, y_values
    
    def create_pivot(self):
        if not self.parse_input_data():
            return
        
        try:
            # Lọc dữ liệu theo filter
            filtered_data = self.get_filtered_data()
            
            # Tạo pivot table
            self.pivot_data, self.x_values, self.y_values = self.create_pivot_table(filtered_data)
            
            # Hiển thị trong treeview
            self.display_pivot_table()
            
            messagebox.showinfo("Thành công", "Đã tạo pivot table thành công!")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi khi tạo pivot table: {str(e)}")
    
    def display_pivot_table(self):
        # Xóa dữ liệu cũ
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not self.pivot_data:
            return
        
        # Thiết lập columns
        columns = ['x_Rows'] + self.y_values
        self.tree['columns'] = columns
        self.tree['show'] = 'headings'
        
        # Thiết lập headers
        for col in columns:
            self.tree.heading(col, text=str(col))
            self.tree.column(col, width=80)
        
        # Thêm dữ liệu
        for x in self.x_values:
            values = [str(x)] + [str(self.pivot_data[x][y]) for y in self.y_values]
            self.tree.insert('', tk.END, values=values)
    
    def on_filter_change(self, event=None):
        if self.raw_data:
            self.create_pivot()
    
    def draw_circle(self):
        if not self.pivot_data:
            messagebox.showwarning("Cảnh báo", "Vui lòng tạo pivot table trước!")
            return
        
        try:
            # Xóa plot cũ
            self.ax.clear()
            
            # Lấy tọa độ X, Y từ pivot table
            x_coords = []
            y_coords = []
            
            for x in self.x_values:
                for y in self.y_values:
                    if self.pivot_data[x][y] != 0:  # Chỉ lấy các điểm có giá trị
                        try:
                            x_coords.append(float(x))
                            y_coords.append(float(y))
                        except ValueError:
                            # Nếu không thể chuyển đổi thành số, sử dụng index
                            x_coords.append(self.x_values.index(x))
                            y_coords.append(self.y_values.index(y))
            
            if not x_coords or not y_coords:
                messagebox.showwarning("Cảnh báo", "Không có dữ liệu để vẽ!")
                return
            
            # Vẽ các điểm
            self.ax.scatter(x_coords, y_coords, c='red', s=50, alpha=0.7, label='Data Points')
            
            # Tính toán đường tròn ngoại tiếp
            if len(x_coords) >= 3:
                center_x = sum(x_coords) / len(x_coords)
                center_y = sum(y_coords) / len(y_coords)
                
                # Tính bán kính (khoảng cách xa nhất từ tâm)
                distances = [math.sqrt((x - center_x)**2 + (y - center_y)**2) 
                           for x, y in zip(x_coords, y_coords)]
                radius = max(distances)
                
                # Vẽ đường tròn
                circle = Circle((center_x, center_y), radius, fill=False, 
                              color='blue', linewidth=2, label=f'Circle (r={radius:.2f})')
                self.ax.add_patch(circle)
                
                # Vẽ tâm
                self.ax.plot(center_x, center_y, 'bo', markersize=8, label='Center')
                
            # Thiết lập plot
            self.ax.set_xlabel('X (x_Rows)')
            self.ax.set_ylabel('Y (y_Columns)')
            self.ax.set_title('Data Points with Circumscribed Circle')
            self.ax.legend()
            self.ax.grid(True, alpha=0.3)
            self.ax.set_aspect('equal', adjustable='box')
            
            # Refresh canvas
            self.canvas.draw()
            
            messagebox.showinfo("Thành công", "Đã vẽ đường tròn ngoại tiếp thành công!")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi khi vẽ đường tròn: {str(e)}")
    
    def clear_data(self):
        # Xóa dữ liệu trong text widgets
        for text_widget in self.text_widgets:
            text_widget.delete("1.0", tk.END)
        
        # Xóa treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Xóa plot
        self.ax.clear()
        self.canvas.draw()
        
        # Reset variables
        self.raw_data = {}
        self.pivot_data = {}
        self.filter_combo['values'] = []
        self.filter_combo.set('')
        
        messagebox.showinfo("Thành công", "Đã xóa tất cả dữ liệu!")

def main():
    root = tk.Tk()
    app = PivotVisualizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
