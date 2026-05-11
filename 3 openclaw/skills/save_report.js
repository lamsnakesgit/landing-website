/**
 * Скилл для сохранения ежедневных и почасовых отчетов пользователя.
 */
import fs from 'fs';
import path from 'path';

export default {
    name: "save_report",
    description: "Сохраняет отчет пользователя (метрики, лиды, выручка, гипотезы, планы) в базу данных или файл статистики business_reports.csv.",
    
    parameters: {
        type: "object",
        properties: {
            report_type: { 
                type: "string", 
                enum: ["hourly", "daily", "custom"],
                description: "Тип отчета: почасовой (hourly), дневной (daily) или произвольный (custom)." 
            },
            revenue: { type: "number", description: "Сумма выручки в долларах." },
            leads: { type: "number", description: "Количество лидов." },
            hypotheses: { type: "string", description: "Текстовое описание протестированных гипотез." },
            summary: { type: "string", description: "Краткая выжимка отчета." }
        },
        required: ["report_type", "summary"]
    },
    
    execute: async (params, context) => {
        try {
            const dataDir = path.join(process.cwd(), 'data');
            const reportsFile = path.join(dataDir, 'business_reports.csv');
            if (!fs.existsSync(dataDir)) fs.mkdirSync(dataDir, { recursive: true });
            
            if (!fs.existsSync(reportsFile)) {
                fs.writeFileSync(reportsFile, "Дата,Время,Тип Отчета,Выручка ($),Лиды,Гипотезы,Общее\n", 'utf8');
            }
            
            const now = new Date();
            const date = now.toISOString().split('T')[0];
            const time = now.toISOString().split('T')[1].split('.')[0];
            
            const csvLine = `${date},${time},${params.report_type},${params.revenue || 0},${params.leads || 0},"${(params.hypotheses || 'Нет').replace(/\n/g, ' ')}","${params.summary.replace(/\n/g, ' ')}"\n`;
            fs.appendFileSync(reportsFile, csvLine, 'utf8');
            
            return {
                status: "success",
                message: "Отчет успешно сохранен в базе статистики.",
                saved_data: { date, time, revenue: params.revenue, leads: params.leads }
            };
        } catch (error) {
            return { status: "error", message: "Ошибка сохранения: " + error.message };
        }
    }
};
